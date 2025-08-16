from fastapi import APIRouter, HTTPException, Query, Depends
from bson import ObjectId
from typing import List, Optional
from datetime import datetime
from models.job import Job
from models.user import User
from database.mongo import get_job_collection, get_database
from auth.auth_utils import get_current_user

router = APIRouter()

@router.post("/create")
async def create_job(job: Job, current_user: User = Depends(get_current_user)):
    """
    Create a new job posting. Only recruiters can create jobs.
    """
    if current_user.role != "recruiter":
        raise HTTPException(status_code=403, detail="Only recruiters can create job postings")
    
    job_collection = get_job_collection()
    job_dict = job.dict()
    job_dict["recruiter_id"] = current_user.username
    job_dict["recruiter_email"] = current_user.email
    job_dict["created_at"] = datetime.utcnow()
    job_dict["status"] = "active"
    
    result = await job_collection.insert_one(job_dict)
    if result.inserted_id:
        return {"message": "Job added successfully", "job_id": str(result.inserted_id)}
    else:
        raise HTTPException(status_code=500, detail="Failed to add job")

@router.get("/", response_model=List[Job])
async def list_jobs(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    location: Optional[str] = None,
    company: Optional[str] = None,
    skills: Optional[List[str]] = Query(None),
    status: Optional[str] = Query(default="active")
):
    """
    Get all active job postings with optional filtering and pagination.
    """
    job_collection = get_job_collection()
    
    # Build query filter
    query = {}
    if status:
        query["status"] = status
    if location:
        query["location"] = {"$regex": location, "$options": "i"}
    if company:
        query["company_name"] = {"$regex": company, "$options": "i"}
    if skills:
        query["skills_required"] = {"$all": skills}
    
    # Execute query with pagination
    cursor = job_collection.find(query) \
        .sort("created_at", -1) \
        .skip(skip) \
        .limit(limit)
    
    jobs = []
    async for job in cursor:
        job["id"] = str(job.pop("_id"))
        jobs.append(Job(**job))
    
    return jobs

@router.get("/{job_id}", response_model=Job)
async def get_job(job_id: str):
    """
    Get a specific job by ID.
    """
    job_collection = get_job_collection()
    
    try:
        job = await job_collection.find_one({"_id": ObjectId(job_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid job ID format")
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job["id"] = str(job.pop("_id"))
    return Job(**job)

@router.put("/{job_id}")
async def update_job(
    job_id: str, 
    job_update: Job, 
    current_user: User = Depends(get_current_user)
):
    """
    Update a job posting. Only the recruiter who created it can update.
    """
    if current_user.role != "recruiter":
        raise HTTPException(status_code=403, detail="Only recruiters can update job postings")
    
    job_collection = get_job_collection()
    
    try:
        existing_job = await job_collection.find_one({"_id": ObjectId(job_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid job ID format")
    
    if not existing_job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if existing_job["recruiter_id"] != current_user.username:
        raise HTTPException(status_code=403, detail="You can only update your own job postings")
    
    update_data = job_update.dict()
    update_data["updated_at"] = datetime.utcnow()
    
    result = await job_collection.update_one(
        {"_id": ObjectId(job_id)},
        {"$set": update_data}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=500, detail="Failed to update job")
    
    return {"message": "Job updated successfully"}

@router.delete("/{job_id}")
async def delete_job(job_id: str, current_user: User = Depends(get_current_user)):
    """
    Delete/deactivate a job posting. Only the recruiter who created it can delete.
    """
    if current_user.role != "recruiter":
        raise HTTPException(status_code=403, detail="Only recruiters can delete job postings")
    
    job_collection = get_job_collection()
    
    try:
        existing_job = await job_collection.find_one({"_id": ObjectId(job_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid job ID format")
    
    if not existing_job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if existing_job["recruiter_id"] != current_user.username:
        raise HTTPException(status_code=403, detail="You can only delete your own job postings")
    
    # Soft delete by setting status to inactive
    result = await job_collection.update_one(
        {"_id": ObjectId(job_id)},
        {"$set": {"status": "inactive", "deleted_at": datetime.utcnow()}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=500, detail="Failed to delete job")
    
    return {"message": "Job deleted successfully"}

@router.get("/{job_id}/applications")
async def get_job_applications(
    job_id: str, 
    current_user: User = Depends(get_current_user)
):
    """
    Get all applications for a specific job. Only the recruiter who posted it can see applications.
    """
    if current_user.role != "recruiter":
        raise HTTPException(status_code=403, detail="Only recruiters can view job applications")
    
    job_collection = get_job_collection()
    db = get_database()
    applications_collection = db.applications
    
    # Verify job exists and belongs to the recruiter
    try:
        job = await job_collection.find_one({"_id": ObjectId(job_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid job ID format")
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job["recruiter_id"] != current_user.username:
        raise HTTPException(status_code=403, detail="You can only view applications for your own job postings")
    
    # Get all applications for this job
    cursor = applications_collection.find({"job_id": job_id}) \
        .sort("applied_at", -1)
    
    applications = []
    async for app in cursor:
        app["id"] = str(app.pop("_id"))
        applications.append(app)
    
    return {
        "job_id": job_id,
        "job_title": job["title"],
        "company_name": job["company_name"],
        "total_applications": len(applications),
        "applications": applications
    }

@router.get("/search/skills")
async def search_jobs_by_skills(
    skills: List[str] = Query(...),
    match_all: bool = Query(default=False),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100)
):
    """
    Search jobs by required skills.
    """
    job_collection = get_job_collection()
    
    # Build skills query
    if match_all:
        # All skills must be present
        skills_query = {"skills_required": {"$all": skills}}
    else:
        # Any of the skills can be present
        skills_query = {"skills_required": {"$in": skills}}
    
    query = {
        "status": "active",
        **skills_query
    }
    
    cursor = job_collection.find(query) \
        .sort("created_at", -1) \
        .skip(skip) \
        .limit(limit)
    
    jobs = []
    async for job in cursor:
        job["id"] = str(job.pop("_id"))
        jobs.append(Job(**job))
    
    return jobs