"""
Message model for storing conversation messages.
"""
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional


class Message(SQLModel, table=True):
    """
    Represents a message in a conversation.
    
    Attributes:
        id: Primary key
        conversation_id: Foreign key to Conversation
        role: Message role ("user" or "assistant")
        content: Message text content
        created_at: Message timestamp
    """
    __tablename__ = "messages"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversations.id", index=True)
    role: str = Field(regex="^(user|assistant)$")
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
