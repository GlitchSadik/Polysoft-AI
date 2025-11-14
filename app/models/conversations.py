"""
Conversation model for tracking chat sessions.
"""
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional


class Conversation(SQLModel, table=True):
    """
    Represents a chat conversation session.
    
    Attributes:
        id: Primary key
        title: Conversation title (first message preview)
        created_at: Conversation start timestamp
        updated_at: Last message timestamp
    """
    __tablename__ = "conversations"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    title: Optional[str] = Field(default=None, max_length=200)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
