"""
Database setup and session management.
"""
from sqlmodel import SQLModel, create_engine, Session
from app.config import DATABASE_URL
import logging

logger = logging.getLogger(__name__)

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False
)


def init_db() -> None:
    """Create all database tables."""
    try:
        SQLModel.metadata.create_all(engine)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


def get_session():
    """Yield a database session."""
    with Session(engine) as session:
        yield session
