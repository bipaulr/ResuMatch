from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class JobCreate(BaseModel):
    """Schema for creating a new job posting"""
    title: str = Field(..., min_length=3, max_length=100)
    description: str = Field(..., min_length=10)
    company_name: str = Field(..., min_length=2, max_length=100)
    skills_required: List[str] = Field(..., min_items=1)
    location: str = Field(..., min_length=2)
    salary_range: Optional[str] = None
    job_type: Optional[str] = Field(None, description="Full-time, Part-time, Contract, etc.")
    experience_level: Optional[str] = None

class Job(JobCreate):
    """Schema for a job in the database"""
    id: Optional[str] = Field(None)
    recruiter_id: str
    recruiter_email: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    status: str = Field(default="active", description="active, filled, or closed")
    
    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }