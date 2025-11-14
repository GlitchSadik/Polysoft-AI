"""
Document management router.
"""
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from sqlmodel import Session
from pathlib import Path
from typing import Dict, Any
import logging
import shutil

from app.db import get_session
from app.config import DOCS_DIR, ALLOWED_EXTENSIONS, MAX_FILE_SIZE
from app.services.document_service import get_document_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/docs", tags=["Documents"])


@router.post("/upload", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    session: Session = Depends(get_session)
) -> Dict[str, Any]:
    """Upload and process a document (PDF or TXT)."""
    logger.info(f"Document upload started: {file.filename}")
    
    try:
        # 1. Validate file type
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Filename is required"
            )
        
        file_path = Path(file.filename)
        file_extension = file_path.suffix.lower()
        
        if file_extension not in ALLOWED_EXTENSIONS:
            logger.warning(f"Invalid file type: {file_extension}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type {file_extension} not allowed. Use: {ALLOWED_EXTENSIONS}"
            )
        
        # 2. Validate file size
        file.file.seek(0, 2)  # Seek to end
        file_size = file.file.tell()
        file.file.seek(0)  # Reset to beginning
        
        if file_size > MAX_FILE_SIZE:
            logger.warning(f"File too large: {file_size} bytes")
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size exceeds maximum of {MAX_FILE_SIZE} bytes"
            )
        
        logger.info(f"File validation passed: {file_extension}, {file_size} bytes")
        
        # 3. Save file to storage/docs/
        save_path = DOCS_DIR / file.filename
        
        # Handle duplicate filenames
        counter = 1
        while save_path.exists():
            stem = file_path.stem
            save_path = DOCS_DIR / f"{stem}_{counter}{file_extension}"
            counter += 1
        
        logger.info(f"Saving file to: {save_path}")
        
        with open(save_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.info(f"File saved successfully: {save_path.name}")
        
        # 4. Process document (extract, chunk, embed, store)
        document_service = get_document_service()
        
        result = document_service.process_document(
            file_path=save_path,
            original_filename=file.filename,
            session=session
        )
        
        logger.info(
            f"Document upload complete: {result['chunk_count']} chunks created"
        )
        
        return {
            "status": "success",
            "message": f"Document '{file.filename}' processed successfully",
            "document_id": result["document_id"],
            "document_name": result["document_name"],
            "line_count": result["line_count"],
            "character_count": result["character_count"],
            "chunk_count": result["chunk_count"]
        }
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"Document upload failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process document: {str(e)}"
        )
    
    finally:
        await file.close()


@router.get("/list", response_model=Dict[str, Any])
async def list_documents(session: Session = Depends(get_session)) -> Dict[str, Any]:
    """
    List all uploaded documents.
    
    Args:
        session: Database session
        
    Returns:
        List of documents with metadata
    """
    try:
        document_service = get_document_service()
        documents = document_service.list_documents(session)
        
        return {
            "count": len(documents),
            "documents": [
                {
                    "id": doc.id,
                    "name": doc.name,
                    "path": doc.path,
                    "created_at": doc.created_at.isoformat()
                }
                for doc in documents
            ]
        }
    
    except Exception as e:
        logger.error(f"Failed to list documents: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/{document_id}", response_model=Dict[str, str])
async def delete_document(
    document_id: int,
    session: Session = Depends(get_session)
) -> Dict[str, str]:
    """
    Delete a document and all its chunks.
    
    Args:
        document_id: ID of document to delete
        session: Database session
        
    Returns:
        Success message
    """
    try:
        document_service = get_document_service()
        deleted = document_service.delete_document(document_id, session)
        
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document {document_id} not found"
            )
        
        logger.info(f"Document {document_id} deleted successfully")
        return {
            "status": "success",
            "message": f"Document {document_id} deleted"
        }
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"Failed to delete document {document_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
