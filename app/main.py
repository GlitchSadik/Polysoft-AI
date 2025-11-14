"""
FastAPI main app for RAG chatbot.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import logging
import sys

# Load environment variables from .env file
load_dotenv()

from app.config import LOG_LEVEL, LOG_FORMAT, LOG_DATE_FORMAT
from app.db import init_db
from app.routers import docs_router, chat_router, health_router


# Configure logging
def setup_logging():
    """Set up logging."""
    # Create logger
    root_logger = logging.getLogger()
    root_logger.setLevel(LOG_LEVEL)
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(LOG_LEVEL)
    
    # Create formatter
    formatter = logging.Formatter(
        fmt=LOG_FORMAT,
        datefmt=LOG_DATE_FORMAT
    )
    console_handler.setFormatter(formatter)
    
    # Add handler to logger
    root_logger.addHandler(console_handler)
    
    # Set third-party loggers to WARNING to reduce noise
    logging.getLogger("chromadb").setLevel(logging.WARNING)
    logging.getLogger("sentence_transformers").setLevel(logging.WARNING)
    logging.getLogger("transformers").setLevel(logging.WARNING)
    logging.getLogger("torch").setLevel(logging.WARNING)
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    
    logging.info("Logging configured successfully")


# Setup logging before anything else
setup_logging()
logger = logging.getLogger(__name__)


# Application lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("=" * 70)
    logger.info("Starting RAG-based Company Policy Chatbot")
    logger.info("=" * 70)
    
    try:
        # Initialize database
        logger.info("Initializing database...")
        init_db()
        
        # Pre-load services (triggers model loading)
        logger.info("Pre-loading services...")
        from app.services.llm_service import get_llm_service
        from app.services.document_service import get_document_service
        from app.services.rag_service import get_rag_service
        
        # Initialize services
        get_llm_service()
        get_document_service()
        get_rag_service()
        
        logger.info("All services initialized successfully")
        logger.info("Application startup complete")
        logger.info("=" * 70)
        
        yield
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}", exc_info=True)
        raise
    
    finally:
        # Shutdown
        logger.info("=" * 70)
        logger.info("Shutting down application")
        logger.info("=" * 70)


# Create FastAPI application
app = FastAPI(
    title="Company Policy Chatbot",
    description="RAG-based chatbot for company policy documents using FastAPI, ChromaDB, and sentence-transformers",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health_router.router)
app.include_router(docs_router.router)
app.include_router(chat_router.router)


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint with API information.
    """
    return {
        "name": "Company Policy Chatbot API",
        "version": "1.0.0",
        "description": "RAG-based chatbot for company policy documents",
        "endpoints": {
            "health": "/health",
            "upload_document": "/docs/upload",
            "list_documents": "/docs/list",
            "chat_query": "/chat/query",
            "conversation_messages": "/chat/conversations/{conversation_id}/messages",
            "docs": "/docs"
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting server with uvicorn")
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level=LOG_LEVEL.lower()
    )
