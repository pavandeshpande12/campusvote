"""
CampusVote - Database Configuration
Simple SQLite database with SQLAlchemy ORM
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# Use /tmp on Render (app directory may not be writable), fallback to local for dev
if os.getenv("RENDER"):
    DB_PATH = "/tmp/evoting.db"
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DB_PATH = os.path.join(BASE_DIR, "evoting.db")

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DB_PATH}")

connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(DATABASE_URL, connect_args=connect_args)

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
