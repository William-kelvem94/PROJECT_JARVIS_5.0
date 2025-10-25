"""
WebSocket routes for real-time chat
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Dict, Set
import json
import asyncio
import logging

from app.core.database import AsyncSessionLocal
from app.core.security import security_manager
from app.models.user import User
from app.models.conversation import Conversation
from app.models.message import Message, MessageRole
from app.services.llm_service import get_llm_service
from app.core.exceptions import AuthenticationException

logger = logging.getLogger(__name__)

router = APIRouter()


class ConnectionManager:
    """
    WebSocket connection manager
    """
    
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self.user_sessions: Dict[WebSocket, str] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str):
        """
        Connect a WebSocket
        """
        await websocket.accept()
        
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        
        self.active_connections[user_id].add(websocket)
        self.user_sessions[websocket] = user_id
        
        logger.info(f"User {user_id} connected. Total connections: {len(self.active_connections[user_id])}")
    
    def disconnect(self, websocket: WebSocket):
        """
        Disconnect a WebSocket
        """
        user_id = self.user_sessions.get(websocket)
        
        if user_id and user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        
        if websocket in self.user_sessions:
            del self.user_sessions[websocket]
        
        logger.info(f"User {user_id} disconnected")
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """
        Send message to specific WebSocket
        """
        await websocket.send_text(message)
    
    async def broadcast_to_user(self, message: str, user_id: str):
        """
        Broadcast message to all user's connections
        """
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                await connection.send_text(message)


# Global connection manager
manager = ConnectionManager()


async def verify_token(token: str, db: AsyncSession) -> User:
    """
    Verify WebSocket token and get user
    """
    try:
        payload = security_manager.decode_token(token)
        user_id = payload.get("sub")
        
        if not user_id:
            raise AuthenticationException("Invalid token")
        
        result = await db.execute(select(User).filter(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user or not user.is_active:
            raise AuthenticationException("Invalid user")
        
        return user
        
    except Exception as e:
        raise AuthenticationException(f"Token verification failed: {str(e)}")


@router.websocket("/chat")
async def websocket_chat(
    websocket: WebSocket,
    token: str = Query(...)
):
    """
    WebSocket endpoint for real-time chat with streaming
    """
    db = AsyncSessionLocal()
    user = None
    
    try:
        # Verify token and get user
        user = await verify_token(token, db)
        
        # Connect WebSocket
        await manager.connect(websocket, user.id)
        
        # Send welcome message
        await manager.send_personal_message(
            json.dumps({
                "type": "connection",
                "status": "connected",
                "message": f"Welcome, {user.username}!",
                "user_id": user.id
            }),
            websocket
        )
        
        llm_service = get_llm_service()
        
        # Main message loop
        while True:
            # Receive message
            data_str = await websocket.receive_text()
            data = json.loads(data_str)
            
            message_type = data.get("type", "chat")
            
            if message_type == "ping":
                # Heartbeat
                await manager.send_personal_message(
                    json.dumps({"type": "pong"}),
                    websocket
                )
                continue
            
            if message_type == "chat":
                # Get conversation
                conversation_id = data.get("conversation_id")
                conversation = None
                
                if conversation_id:
                    result = await db.execute(
                        select(Conversation).filter(
                            Conversation.id == conversation_id,
                            Conversation.user_id == user.id
                        )
                    )
                    conversation = result.scalar_one_or_none()
                
                if not conversation:
                    # Create new conversation
                    conversation = Conversation(
                        user_id=user.id,
                        title=data.get("title", "New Conversation"),
                        model_name=data.get("model", llm_service.default_model)
                    )
                    db.add(conversation)
                    await db.commit()
                    await db.refresh(conversation)
                    
                    # Send conversation created event
                    await manager.send_personal_message(
                        json.dumps({
                            "type": "conversation_created",
                            "conversation_id": conversation.id
                        }),
                        websocket
                    )
                
                # Save user message
                user_message = Message(
                    conversation_id=conversation.id,
                    role=MessageRole.USER,
                    content=data.get("message", ""),
                    model_name=conversation.model_name
                )
                db.add(user_message)
                await db.commit()
                
                # Get conversation history
                result = await db.execute(
                    select(Message)
                    .filter(Message.conversation_id == conversation.id)
                    .order_by(Message.created_at)
                )
                messages = result.scalars().all()
                
                # Build LLM messages
                llm_messages = []
                for msg in messages:
                    llm_messages.append({
                        "role": msg.role.value,
                        "content": msg.content
                    })
                
                # Send message start event
                await manager.send_personal_message(
                    json.dumps({
                        "type": "message_start",
                        "conversation_id": conversation.id
                    }),
                    websocket
                )
                
                # Stream response
                full_response = ""
                async for chunk in await llm_service.chat_stream(
                    messages=llm_messages,
                    model=data.get("model"),
                    temperature=data.get("temperature", 0.7)
                ):
                    full_response += chunk
                    
                    # Send chunk
                    await manager.send_personal_message(
                        json.dumps({
                            "type": "message_chunk",
                            "content": chunk,
                            "conversation_id": conversation.id
                        }),
                        websocket
                    )
                
                # Save assistant message
                assistant_message = Message(
                    conversation_id=conversation.id,
                    role=MessageRole.ASSISTANT,
                    content=full_response,
                    model_name=conversation.model_name
                )
                db.add(assistant_message)
                await db.commit()
                await db.refresh(assistant_message)
                
                # Send message end event
                await manager.send_personal_message(
                    json.dumps({
                        "type": "message_end",
                        "conversation_id": conversation.id,
                        "message_id": assistant_message.id
                    }),
                    websocket
                )
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("WebSocket disconnected normally")
    
    except AuthenticationException as e:
        logger.error(f"Authentication error: {str(e)}")
        await websocket.close(code=1008, reason="Authentication failed")
    
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}", exc_info=True)
        try:
            await manager.send_personal_message(
                json.dumps({
                    "type": "error",
                    "message": str(e)
                }),
                websocket
            )
        except:
            pass
        manager.disconnect(websocket)
    
    finally:
        await db.close()


@router.websocket("/voice")
async def websocket_voice(
    websocket: WebSocket,
    token: str = Query(...)
):
    """
    WebSocket endpoint for voice chat
    """
    # TODO: Implement voice chat with Whisper STT and TTS
    await websocket.accept()
    await websocket.send_text(json.dumps({
        "type": "error",
        "message": "Voice chat not yet implemented"
    }))
    await websocket.close()

