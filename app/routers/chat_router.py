"""
Chat router for RAG queries.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import logging

from app.db import get_session
from app.services.rag_service import get_rag_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["Chat"])


# Request/Response models
class ChatRequest(BaseModel):
    """Chat query request."""
    message: str = Field(..., min_length=1, description="User's question or message")
    conversation_id: Optional[int] = Field(None, description="Existing conversation ID")


class Citation(BaseModel):
    """Citation for source reference."""
    doc_name: str
    section_title: str
    start_line: int
    end_line: int
    snippet: str


class ChatResponse(BaseModel):
    """Chat query response."""
    conversation_id: int
    answer: str
    citations: List[Citation]


@router.post("/query", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def chat_query(
    request: ChatRequest,
    session: Session = Depends(get_session)
) -> ChatResponse:
    """Process a chat query using RAG."""
        session: Database session
        
    Returns:
        Response with conversation_id, answer, and citations
    """
    logger.info(
        f"Chat query received: conversation_id={request.conversation_id}, "
        f"message_length={len(request.message)}"
    )
    
    try:
        rag_service = get_rag_service()
        
        result = rag_service.query(
            message=request.message,
            conversation_id=request.conversation_id,
            session=session
        )
        
        logger.info(
            f"Chat query completed: conversation_id={result['conversation_id']}, "
            f"citations_count={len(result['citations'])}"
        )
        
        return ChatResponse(
            conversation_id=result["conversation_id"],
            answer=result["answer"],
            citations=[Citation(**c) for c in result["citations"]]
        )
    
    except Exception as e:
        logger.error(f"Chat query failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process chat query: {str(e)}"
        )


@router.get("/conversations/{conversation_id}/messages", response_model=Dict[str, Any])
async def get_conversation_messages(
    conversation_id: int,
    session: Session = Depends(get_session)
) -> Dict[str, Any]:
    """
    Get all messages for a conversation.
    
    Args:
        conversation_id: Conversation ID
        session: Database session
        
    Returns:
        List of messages with metadata
    """
    try:
        rag_service = get_rag_service()
        messages = rag_service.get_conversation_messages(conversation_id, session)
        
        return {
            "conversation_id": conversation_id,
            "message_count": len(messages),
            "messages": messages
        }
    
    except Exception as e:
        logger.error(
            f"Failed to get conversation {conversation_id} messages: {e}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/conversations", response_model=List[Dict[str, Any]])
async def list_conversations(
    limit: int = 50,
    session: Session = Depends(get_session)
) -> List[Dict[str, Any]]:
    """
    List all conversations ordered by most recent.
    
    Args:
        limit: Maximum number of conversations to return
        session: Database session
        
    Returns:
        List of conversations
    """
    from app.models.conversations import Conversation
    from sqlmodel import select
    
    try:
        statement = select(Conversation).order_by(
            Conversation.updated_at.desc()
        ).limit(limit)
        conversations = session.exec(statement).all()
        
        return [
            {
                "id": conv.id,
                "title": conv.title,
                "created_at": conv.created_at.isoformat(),
                "updated_at": conv.updated_at.isoformat()
            }
            for conv in conversations
        ]
    
    except Exception as e:
        logger.error(f"Failed to list conversations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
