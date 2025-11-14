"""
Document model for storing uploaded policy documents.
"""
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional


class Document(SQLModel, table=True):
    """
    Represents an uploaded policy document.
    
    Attributes:
        id: Primary key
        name: Original filename
        path: Storage path relative to DOCS_DIR
        created_at: Upload timestamp
    """
    __tablename__ = "documents"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    path: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
