"""
App configuration and constants.
"""
import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent.parent
STORAGE_DIR = BASE_DIR / "storage"
DOCS_DIR = STORAGE_DIR / "docs"
CHROMA_DB_DIR = STORAGE_DIR / "chroma_db"

DOCS_DIR.mkdir(parents=True, exist_ok=True)
CHROMA_DB_DIR.mkdir(parents=True, exist_ok=True)

# Database settings
DATABASE_URL = f"sqlite:///{BASE_DIR}/policy_chatbot.db"

# ChromaDB settings
CHROMA_COLLECTION_NAME = "policy_documents"

# Embedding model
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# Chunking settings
CHUNK_SIZE = 900  # Target chunk size in characters
CHUNK_OVERLAP = 100  # Overlap between chunks
SEPARATORS = ["\n\n", "\n", " "]  # Priority order for splitting

# Section heading detection regex
SECTION_HEADING_PATTERN = r"^\d+\.\s+.*"

# RAG settings
RETRIEVAL_TOP_K = 4  # Number of chunks to retrieve
CONVERSATION_HISTORY_LENGTH = 5  # Number of messages to include in context

# Logging settings
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# File upload settings
ALLOWED_EXTENSIONS = {".pdf", ".txt"}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
OPENAI_MAX_TOKENS = int(os.getenv("OPENAI_MAX_TOKENS", "1000"))
