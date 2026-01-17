"""
Job model - tracks background job execution
"""
from sqlalchemy import Column, String, Text, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from app.db.database import Base


class Job(Base):
    """Job model for tracking background tasks"""
    __tablename__ = "jobs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=True)  # For multi-user support
    job_type = Column(String, nullable=False, index=True)  # discover, enrich, compose, send
    params = Column(JSON)  # Job parameters (keywords, location, etc.)
    status = Column(String, default="pending", index=True)  # pending/running/completed/failed
    result = Column(JSON)  # Job result data
    error_message = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Job(id={self.id}, type={self.job_type}, status={self.status})>"

