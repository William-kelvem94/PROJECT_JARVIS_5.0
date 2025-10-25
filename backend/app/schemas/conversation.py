"""Conversation and message schemas"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class MessageRole(str, Enum):
    """Message role enumeration"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class MessageBase(BaseModel):
    """Base message schema"""
    role: MessageRole
    content: str = Field(..., min_length=1)


class MessageCreate(MessageBase):
    """Schema for message creation"""
    conversation_id: str


class MessageResponse(MessageBase):
    """Schema for message response"""
    id: str
    conversation_id: str
    model_name: Optional[str] = None
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    metadata: Dict[str, Any] = {}
    created_at: datetime
    
    class Config:
        from_attributes = True


class ConversationBase(BaseModel):
    """Base conversation schema"""
    title: str = Field(default="New Conversation", max_length=255)
    model_name: str = Field(default="llama2", max_length=100)


class ConversationCreate(ConversationBase):
    """Schema for conversation creation"""
    pass


class ConversationUpdate(BaseModel):
    """Schema for conversation update"""
    title: Optional[str] = None
    model_name: Optional[str] = None


class ConversationResponse(ConversationBase):
    """Schema for conversation response"""
    id: str
    user_id: str
    metadata: Dict[str, Any] = {}
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ConversationWithMessages(ConversationResponse):
    """Schema for conversation with messages"""
    messages: List[MessageResponse] = []


class ChatRequest(BaseModel):
    """Schema for chat request"""
    message: str = Field(..., min_length=1, max_length=4096)
    conversation_id: Optional[str] = None
    model: Optional[str] = None
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    stream: bool = False


class ChatResponse(BaseModel):
    """Schema for chat response"""
    message: str
    conversation_id: str
    message_id: str
    model: str
    tokens_used: int = 0

