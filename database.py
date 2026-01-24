"""
CampusVote - Database Configuration
Simple SQLite database with SQLAlchemy ORM
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# Get the directory where this script is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "evoting.db")

# Database URL - uses SQLite with absolute path
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DB_PATH}")

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db():
    """Get database session"""
    return SessionLocal()


def init_db():
    """Initialize database tables"""
    from models import Candidate, Vote
    Base.metadata.create_all(bind=engine)


def close_db(db):
    """Close database session"""
    if db:
        db.close()
