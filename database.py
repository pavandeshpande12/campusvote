"""
CampusVote - Database Configuration
Simple SQLite database with SQLAlchemy ORM
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# Database URL - uses SQLite
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///evoting.db")

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
    """Initialize database tables - drops old tables if schema changed"""
    from models import Candidate, Vote
    from sqlalchemy import inspect

    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()

    # If old schema exists (users, elections tables), drop everything and start fresh
    if "users" in existing_tables or "elections" in existing_tables:
        Base.metadata.drop_all(bind=engine)

    Base.metadata.create_all(bind=engine)


def close_db(db):
    """Close database session"""
    if db:
        db.close()
