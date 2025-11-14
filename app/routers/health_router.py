"""
Health check router.
"""
from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from typing import Dict, Any
import logging

from app.db import get_session
from app.models.documents import Document
from app.services.document_service import get_document_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("", response_model=Dict[str, Any])
async def health_check(session: Session = Depends(get_session)) -> Dict[str, Any]:
    """Check system health."""
    logger.info("Health check requested")
    
    status = {
        "status": "ok",
        "db": "ok",
        "chroma": "ok",
        "details": {}
    }
    
    # Check database
    try:
        # Try to query the Document table
        statement = select(Document).limit(1)
        session.exec(statement).first()
        
        logger.debug("Database check passed")
        status["db"] = "ok"
        status["details"]["db_message"] = "Connected and operational"
    
    except Exception as e:
        logger.error(f"Database check failed: {e}")
        status["db"] = "error"
        status["status"] = "degraded"
        status["details"]["db_error"] = str(e)
    
    # Check ChromaDB
    try:
        document_service = get_document_service()
        
        # Try to list collections
        collections = document_service.chroma_client.list_collections()
        collection_names = [c.name for c in collections]
        
        logger.debug(f"ChromaDB check passed. Collections: {collection_names}")
        status["chroma"] = "ok"
        status["details"]["chroma_collections"] = collection_names
        status["details"]["chroma_message"] = "Connected and operational"
    
    except Exception as e:
        logger.error(f"ChromaDB check failed: {e}")
        status["chroma"] = "error"
        status["status"] = "degraded"
        status["details"]["chroma_error"] = str(e)
    
    logger.info(f"Health check result: {status['status']}")
    return status
