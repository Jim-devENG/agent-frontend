"""
Social Media Outreach Models

Separate from Website Outreach - parallel system with no shared logic.
"""
from sqlalchemy import Column, String, Text, Integer, Boolean, JSON, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from enum import Enum
from app.db.database import Base


class SocialPlatform(str, Enum):
    """Supported social media platforms"""
    LINKEDIN = "linkedin"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"


class QualificationStatus(str, Enum):
    """Profile qualification status"""
    PENDING = "pending"
    QUALIFIED = "qualified"
    REJECTED = "rejected"


class MessageStatus(str, Enum):
    """Message sending status"""
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    DELIVERED = "delivered"
    READ = "read"


class SocialProfile(Base):
    """Social media profile for outreach"""
    __tablename__ = "social_profiles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    platform = Column(SQLEnum(SocialPlatform), nullable=False, index=True)
    handle = Column(String, nullable=False, index=True)  # @username or profile identifier
    profile_url = Column(Text, nullable=False, unique=True, index=True)
    display_name = Column(String)
    bio = Column(Text)
    followers_count = Column(Integer, default=0)
    location = Column(String)
    is_business = Column(Boolean, default=False, nullable=False)
    qualification_status = Column(SQLEnum(QualificationStatus), nullable=False, server_default=QualificationStatus.PENDING.value, index=True)
    discovery_job_id = Column(UUID(as_uuid=True), ForeignKey("social_discovery_jobs.id"), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    discovery_job = relationship("SocialDiscoveryJob", back_populates="profiles")
    drafts = relationship("SocialDraft", back_populates="profile", cascade="all, delete-orphan")
    messages = relationship("SocialMessage", back_populates="profile", cascade="all, delete-orphan")


class SocialDiscoveryJob(Base):
    """Discovery job for social profiles"""
    __tablename__ = "social_discovery_jobs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    platform = Column(SQLEnum(SocialPlatform), nullable=False, index=True)
    filters = Column(JSON)  # Search filters: keywords, location, hashtags, etc.
    status = Column(String, nullable=False, default="pending", index=True)  # pending, running, completed, failed
    results_count = Column(Integer, default=0)
    error_message = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    profiles = relationship("SocialProfile", back_populates="discovery_job")


class SocialDraft(Base):
    """Draft message for social profile"""
    __tablename__ = "social_drafts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    profile_id = Column(UUID(as_uuid=True), ForeignKey("social_profiles.id"), nullable=False, index=True)
    platform = Column(SQLEnum(SocialPlatform), nullable=False)
    draft_body = Column(Text, nullable=False)
    is_followup = Column(Boolean, default=False, nullable=False)
    sequence_index = Column(Integer, default=0, nullable=False)  # 0 = initial, 1+ = follow-up
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    profile = relationship("SocialProfile", back_populates="drafts")


class SocialMessage(Base):
    """Sent message to social profile"""
    __tablename__ = "social_messages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    profile_id = Column(UUID(as_uuid=True), ForeignKey("social_profiles.id"), nullable=False, index=True)
    platform = Column(SQLEnum(SocialPlatform), nullable=False)
    message_body = Column(Text, nullable=False)
    status = Column(SQLEnum(MessageStatus), nullable=False, server_default=MessageStatus.PENDING.value, index=True)
    sent_at = Column(DateTime(timezone=True))
    error_message = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    profile = relationship("SocialProfile", back_populates="messages")

