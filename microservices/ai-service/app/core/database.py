import os
from contextlib import contextmanager
from typing import Generator

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker, Session

# Load environment variables from .env
load_dotenv()

# Patch pgvector Vector._from_db for psycopg3 compatibility
try:
    import pgvector.vector
    _orig_from_db = pgvector.vector.Vector._from_db
    def _patched_from_db(cls, value):
        if isinstance(value, list):
            return value
        return _orig_from_db(value)
    pgvector.vector.Vector._from_db = classmethod(_patched_from_db)
except Exception:
    pass

def get_database_url() -> str:
    """Construct or retrieve PostgreSQL DATABASE_URL from environment variables."""
    url = os.getenv("DATABASE_URL")
    if url:
        return url

    user = os.getenv("POSTGRES_USER", "postgres")
    password = os.getenv("POSTGRES_PASSWORD", "postgres")
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    db_name = os.getenv("POSTGRES_DB", "ai_service_db")
    return f"postgresql://{user}:{password}@{host}:{port}/{db_name}"

DATABASE_URL = get_database_url()

# SQLAlchemy Engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

# Session Factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# Declarative Base for ORM models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """FastAPI Dependency Generator for providing database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """Context manager for standalone/script database sessions with auto-commit and rollback."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


# Alias for intuitive context manager usage (with db_session() as db:)
db_session = get_db_context


def check_db_connection() -> bool:
    """Check database connection health."""
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
