"""
Chunk model for storing document chunks with metadata.
"""
from sqlmodel import SQLModel, Field
from typing import Optional


class Chunk(SQLModel, table=True):
    """
    Represents a text chunk extracted from a document.
    
    Attributes:
        id: Primary key
        document_id: Foreign key to Document
        chunk_id: Unique identifier for ChromaDB
        content: The actual text content
        start_line: Starting line number in original document
        end_line: Ending line number in original document
        section_title: Section heading this chunk belongs to
    """
    __tablename__ = "chunks"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    document_id: int = Field(foreign_key="documents.id", index=True)
    chunk_id: str = Field(unique=True, index=True)
    content: str
    start_line: int
    end_line: int
    section_title: str = Field(default="")
