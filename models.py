"""
CampusVote - Simplified Database Models
Only 2 tables: Candidate and Vote
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from datetime import datetime, timezone
from database import Base


def utc_now():
    """Get current UTC time"""
    return datetime.now(timezone.utc)


class Candidate(Base):
    """Candidate model for election candidates"""
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    position = Column(String(100), nullable=False, default="President")
    description = Column(Text)
    photo = Column(String(255))
    vote_count = Column(Integer, default=0)

    def __repr__(self):
        return f"<Candidate {self.name}>"


class Vote(Base):
    """Vote model to track votes - uses email for simplicity"""
    __tablename__ = "votes"

    id = Column(Integer, primary_key=True, index=True)
    voter_email = Column(String(100), nullable=False, unique=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)
    voted_at = Column(DateTime, default=utc_now)

    def __repr__(self):
        return f"<Vote email={self.voter_email} candidate={self.candidate_id}>"
