"""
Pydantic schemas for job-related endpoints
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID


class JobCreateRequest(BaseModel):
    """Request schema for creating a discovery job"""
    keywords: Optional[str] = Field(None, description="Search keywords (optional if categories provided)")
    locations: Optional[list[str]] = Field(None, description="Location filters (e.g., ['usa', 'canada'])")
    max_results: int = Field(100, ge=1, le=1000, description="Maximum number of results")
    categories: Optional[list[str]] = Field(None, description="Category filters")


class JobResponse(BaseModel):
    """Response schema for job status"""
    id: UUID
    job_type: str
    status: str
    params: Optional[Dict[str, Any]] = None
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class JobStatusResponse(BaseModel):
    """Response schema for job status check"""
    id: UUID
    status: str
    progress: Optional[Dict[str, Any]] = None
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None


class JobCreate(BaseModel):
    """Request schema for creating a job"""
    job_type: str
    params: Optional[Dict[str, Any]] = None


class JobListResponse(BaseModel):
    """Response schema for listing jobs"""
    data: List[JobResponse]
    total: int
    skip: int
    limit: int

