"""
Chat routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.models.conversation import Conversation
from app.models.message import Message, MessageRole
from app.schemas.conversation import ChatRequest, ChatResponse
from app.services.llm_service import get_llm_service

router = APIRouter()


@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Send a chat message and get response
    """
    llm_service = get_llm_service()
    
    # Get or create conversation
    conversation = None
    if request.conversation_id:
        result = await db.execute(
            select(Conversation).filter(
                Conversation.id == request.conversation_id,
                Conversation.user_id == current_user.id
            )
        )
        conversation = result.scalar_one_or_none()
        
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
    else:
        # Create new conversation
        conversation = Conversation(
            user_id=current_user.id,
            model_name=request.model or llm_service.default_model
        )
        db.add(conversation)
        await db.commit()
        await db.refresh(conversation)
    
    # Save user message
    user_message = Message(
        conversation_id=conversation.id,
        role=MessageRole.USER,
        content=request.message,
        model_name=request.model or llm_service.default_model
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
    
    # Build messages for LLM
    llm_messages = []
    for msg in messages:
        llm_messages.append({
            "role": msg.role.value,
            "content": msg.content
        })
    
    # Generate response
    if request.stream:
        # TODO: Implement streaming response
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Streaming not yet implemented in REST API. Use WebSocket instead."
        )
    else:
        response_text = await llm_service.chat(
            messages=llm_messages,
            model=request.model,
            temperature=request.temperature
        )
    
    # Save assistant message
    assistant_message = Message(
        conversation_id=conversation.id,
        role=MessageRole.ASSISTANT,
        content=response_text,
        model_name=request.model or llm_service.default_model
    )
    db.add(assistant_message)
    await db.commit()
    await db.refresh(assistant_message)
    
    return ChatResponse(
        message=response_text,
        conversation_id=conversation.id,
        message_id=assistant_message.id,
        model=assistant_message.model_name,
        tokens_used=0  # TODO: Track token usage
    )

