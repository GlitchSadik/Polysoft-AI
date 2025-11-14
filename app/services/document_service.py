"""
Document ingestion service for uploads, extraction, chunking, and vector storage.
"""
from pathlib import Path
from typing import Dict, Any
from sqlmodel import Session, select
import chromadb
from chromadb.config import Settings
import uuid
import logging

from app.config import DOCS_DIR, CHROMA_DB_DIR, CHROMA_COLLECTION_NAME
from app.models.documents import Document
from app.models.chunks import Chunk
from app.utils.pdf_utils import extract_text
from app.utils.chunking import chunk_with_sections
from app.services.llm_service import get_llm_service

logger = logging.getLogger(__name__)


class DocumentService:
    """
    Handles document upload, chunking, and embedding.
    """
    
    def __init__(self):
        logger.info("Initializing DocumentService")
        try:
            self.chroma_client = chromadb.PersistentClient(
                path=str(CHROMA_DB_DIR),
                settings=Settings(anonymized_telemetry=False)
            )
            self.collection = self.chroma_client.get_or_create_collection(
                name=CHROMA_COLLECTION_NAME,
                metadata={"description": "Document chunks"}
            )
            logger.info(f"ChromaDB collection '{CHROMA_COLLECTION_NAME}' ready")
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            raise
        self.llm_service = get_llm_service()
    
    def process_document(
        self,
        file_path: Path,
        original_filename: str,
        session: Session
    ) -> Dict[str, Any]:
        """
        Extracts text, chunks, embeds, and stores a document.
        Returns a summary dict.
        """
        logger.info(f"Processing document: {original_filename}")
        try:
            full_text = extract_text(file_path)
            if not full_text or not full_text.strip():
                raise ValueError("No text content extracted from document")
            line_count = len(full_text.splitlines())
            logger.info(f"Extracted {line_count} lines, {len(full_text)} characters")
            document = Document(
                name=original_filename,
                path=str(file_path.relative_to(DOCS_DIR.parent))
            )
            session.add(document)
            session.commit()
            session.refresh(document)
            logger.info(f"Created document record with ID: {document.id}")
            chunks_data = chunk_with_sections(full_text)
            if not chunks_data:
                raise ValueError("No chunks created from document")
            logger.info(f"Created {len(chunks_data)} chunks")
            chunk_ids = []
            chunk_contents = []
            chunk_metadatas = []
            for idx, (content, start_line, end_line, section_title) in enumerate(chunks_data):
                chunk_id = f"doc_{document.id}_chunk_{idx}"
                chunk_ids.append(chunk_id)
                chunk_contents.append(content)
                metadata = {
                    "chunk_id": chunk_id,
                    "doc_name": original_filename,
                    "section_title": section_title,
                    "start_line": start_line,
                    "end_line": end_line,
                    "document_id": document.id
                }
                chunk_metadatas.append(metadata)
                chunk = Chunk(
                    document_id=document.id,
                    chunk_id=chunk_id,
                    content=content,
                    start_line=start_line,
                    end_line=end_line,
                    section_title=section_title
                )
                session.add(chunk)
            session.commit()
            logger.info(f"Saved {len(chunks_data)} chunks to database")
            embeddings = self.llm_service.embed_batch(chunk_contents)
            if len(embeddings) != len(chunk_ids):
                raise ValueError("Embedding count mismatch")
            logger.info(f"Generated {len(embeddings)} embeddings")
            self.collection.upsert(
                ids=chunk_ids,
                embeddings=embeddings,
                documents=chunk_contents,
                metadatas=chunk_metadatas
            )
            logger.info(f"Successfully upserted {len(chunk_ids)} chunks to ChromaDB")
            result = {
                "document_id": document.id,
                "document_name": original_filename,
                "line_count": line_count,
                "character_count": len(full_text),
                "chunk_count": len(chunks_data),
                "status": "success"
            }
            logger.info(f"Document processing complete: {result}")
            return result
        except Exception as e:
            logger.error(f"Failed to process document {original_filename}: {e}")
            raise
    
    def get_document_by_id(self, document_id: int, session: Session) -> Document:
        """Get a document by its ID."""
        statement = select(Document).where(Document.id == document_id)
        return session.exec(statement).first()
    
    def list_documents(self, session: Session, limit: int = 100) -> list:
        """Return a list of documents (max: limit)."""
        statement = select(Document).limit(limit)
        return list(session.exec(statement))
    
    def delete_document(self, document_id: int, session: Session) -> bool:
        """Delete a document and its chunks."""
        try:
            document = self.get_document_by_id(document_id, session)
            if not document:
                return False
            chunk_statement = select(Chunk).where(Chunk.document_id == document_id)
            chunks = list(session.exec(chunk_statement))
            if chunks:
                chunk_ids = [chunk.chunk_id for chunk in chunks]
                self.collection.delete(ids=chunk_ids)
                logger.info(f"Deleted {len(chunk_ids)} chunks from ChromaDB")
            for chunk in chunks:
                session.delete(chunk)
            try:
                file_path = Path(document.path)
                if file_path.exists():
                    file_path.unlink()
                    logger.info(f"Deleted file: {file_path}")
            except Exception as e:
                logger.warning(f"Failed to delete file: {e}")
            session.delete(document)
            session.commit()
            logger.info(f"Deleted document {document_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete document {document_id}: {e}")
            raise


# Global singleton instance
_document_service_instance = None


def get_document_service() -> DocumentService:
    """Return the global DocumentService instance."""
    global _document_service_instance
    if _document_service_instance is None:
        logger.info("Initializing global DocumentService")
        _document_service_instance = DocumentService()
    return _document_service_instance
