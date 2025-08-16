from fastapi import APIRouter, Depends, HTTPException
from models.job import JobCreate
from models.user import User
from database.mongo import get_job_collection, get_database
from utils.parser.gemini_client import get_gemini_response, get_gemini_mock_interview_response
from auth.dependencies import get_current_recruiter
from datetime import datetime
from bson import ObjectId
import json

router = APIRouter()

@router.get("/dashboard")
async def recruiter_dashboard(current_user: User = Depends(get_current_recruiter)):
    """Recruiter dashboard with user-specific data."""
    try:
        db = get_database()
        job_collection = get_job_collection()
        applications_collection = db.applications
        
        # Count active jobs posted by this recruiter
        active_jobs = await job_collection.count_documents({
            "recruiter_id": current_user.username,
            "status": "active"
        })
        
        # Count total applications received
        total_applications = await applications_collection.count_documents({
            "recruiter_id": current_user.username
        })
        
        # Count pending applications (mock interviews)
        pending_interviews = await applications_collection.count_documents({
            "recruiter_id": current_user.username,
            "status": "interview_scheduled"
        })
        
        return {
            "message": f"Welcome to your dashboard, {current_user.username}!",
            "role": current_user.role,
            "email": current_user.email,
            "stats": {
                "active_jobs": active_jobs,
                "total_applications": total_applications,
                "pending_interviews": pending_interviews,
                "unread_messages": 0  # This would come from chat system
            },
            "recent_activity": [
                {
                    "id": "1",
                    "type": "application",
                    "title": "New application received",
                    "timestamp": "2024-01-15T10:00:00Z"
                }
            ]
        }
    except Exception as e:
        print(f"Error getting recruiter dashboard: {e}")
        return {
            "message": f"Welcome to your dashboard, {current_user.username}!",
            "role": current_user.role,
            "email": current_user.email,
            "stats": {
                "active_jobs": 0,
                "total_applications": 0,
                "pending_interviews": 0,
                "unread_messages": 0
            },
            "recent_activity": []
        }

@router.get("/stats")
async def get_recruiter_stats(current_user: User = Depends(get_current_recruiter)):
    """Get recruiter statistics for dashboard."""
    try:
        db = get_database()
        job_collection = get_job_collection()
        applications_collection = db.applications
        
        # Count jobs and applications
        active_jobs = await job_collection.count_documents({
            "recruiter_id": current_user.username,
            "status": "active"
        })
        
        total_applications = await applications_collection.count_documents({
            "recruiter_id": current_user.username
        })
        
        pending_interviews = await applications_collection.count_documents({
            "recruiter_id": current_user.username,
            "status": "interview_scheduled"
        })
        
        return {
            "active_jobs": active_jobs,
            "total_applications": total_applications,
            "pending_interviews": pending_interviews,
            "unread_messages": 0
        }
    except Exception as e:
        print(f"Error getting recruiter stats: {e}")
        return {
            "active_jobs": 0,
            "total_applications": 0,
            "pending_interviews": 0,
            "unread_messages": 0
        }

# Recruiter posts a job
@router.post("/post-job")
async def post_job(job: JobCreate, current_user: User = Depends(get_current_recruiter)):
    job_collection = get_job_collection()
    job_dict = job.dict()
    # Add recruiter information to the job
    job_dict["recruiter_id"] = current_user.username
    job_dict["recruiter_email"] = current_user.email
    job_dict["created_at"] = datetime.utcnow()
    job_dict["status"] = "active"  # Set default status
    
    result = await job_collection.insert_one(job_dict)
    if result.inserted_id:
        return {"message": "Job posted successfully", "job_id": str(result.inserted_id)}
    else:
        raise HTTPException(status_code=500, detail="Failed to post job")

# Recruiter views all their jobs
@router.get("/my-jobs")
async def my_jobs(current_user: User = Depends(get_current_recruiter)):
    job_collection = get_job_collection()
    # Only return jobs posted by the current recruiter
    jobs = await job_collection.find(
        {"recruiter_id": current_user.username}
    ).to_list(length=100)
    
    for job in jobs:
        job["_id"] = str(job["_id"])
    return {
        "recruiter": current_user.username,
        "total_jobs": len(jobs),
        "jobs": jobs
    }

# AI Mock Interview Endpoint
@router.post("/mock-interview")
async def mock_interview(
    resume_text: str,
    job_description: str,
    current_user: User = Depends(get_current_recruiter)
):
    prompt = f"""
    You are an experienced technical recruiter conducting an interview. Based on the candidate's resume and job requirements:
    
    Resume: {resume_text}
    Job Description: {job_description}
    
    Please provide interview questions and analysis. You MUST respond in valid JSON format only, no additional text.
    
    {{
        "technical_questions": [
            "Question 1 about specific technical skills",
            "Question 2 about frameworks/tools",
            "Question 3 about problem-solving",
            "Question 4 about experience with specific technologies",
            "Question 5 about system design or architecture"
        ],
        "behavioral_questions": [
            "Tell me about a challenging project you worked on",
            "How do you handle tight deadlines and pressure?",
            "Describe a time when you had to learn a new technology quickly"
        ],
        "fit_analysis": "Brief analysis of candidate's fit for the role based on resume and job requirements",
        "focus_areas": [
            "Technical expertise area 1",
            "Soft skills area",
            "Experience validation area"
        ]
    }}
    """
    
    try:
        # Use the specialized function for better JSON handling
        parsed_response = await get_gemini_mock_interview_response(resume_text, job_description)
        
        # Validate the response structure
        required_keys = ["technical_questions", "behavioral_questions", "fit_analysis", "focus_areas"]
        for key in required_keys:
            if key not in parsed_response:
                parsed_response[key] = f"Error: Missing {key} in AI response"
        
        return parsed_response
        
    except Exception as e:
        print(f"Error in mock_interview: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate interview questions: {str(e)}"
        )

@router.get("/chat-rooms")
async def get_recruiter_chat_rooms(current_user: User = Depends(get_current_recruiter)):
    """Get all chat rooms for the current recruiter."""
    db = get_database()
    chat_rooms_collection = db.chat_rooms
    messages_collection = db.messages
    job_collection = get_job_collection()
    
    # Find all chat rooms where the recruiter is a participant
    rooms = await chat_rooms_collection.find({
        "recruiter_id": current_user.username,
        "is_active": True
    }).to_list(length=100)
    
    # Enrich room data with job info and last message
    enriched_rooms = []
    for room in rooms:
        room_id = str(room["_id"])
        
        # Get job details
        job = await job_collection.find_one({"_id": ObjectId(room["job_id"])})
        
        # Get last message
        last_message = await messages_collection.find_one(
            {"room_id": room_id},
            sort=[("timestamp", -1)]
        )
        
        # Count unread messages for this recruiter
        unread_count = await messages_collection.count_documents({
            "room_id": room_id,
            "receiver_id": current_user.username,
            "read": False
        })
        
        enriched_room = {
            "id": room_id,
            "job_id": room["job_id"],
            "student_id": room["student_id"],
            "job_title": job["title"] if job else "Unknown Job",
            "company_name": job["company_name"] if job else "Unknown Company",
            "created_at": room["created_at"].isoformat(),
            "last_message": {
                "content": last_message["content"] if last_message else None,
                "sender_id": last_message["sender_id"] if last_message else None,
                "timestamp": last_message["timestamp"].isoformat() if last_message else None
            } if last_message else None,
            "unread_count": unread_count,
            "participants": [current_user.username, room["student_id"]]
        }
        enriched_rooms.append(enriched_room)
    
    return {"chat_rooms": enriched_rooms}

# Chat history persistence (with MongoDB and auth)
@router.get("/chat-history/{room_id}")
async def chat_history(
    room_id: str,
    current_user: User = Depends(get_current_recruiter)
):
    db = get_database()
    messages_collection = db.messages
    
    # Only fetch messages where the recruiter is involved
    messages = await messages_collection.find({
        "room_id": room_id,
        "$or": [
            {"sender_id": current_user.username},
            {"receiver_id": current_user.username}
        ]
    }).sort("timestamp", 1).to_list(length=100)
    
    for msg in messages:
        msg["_id"] = str(msg["_id"])
        
    return {
        "room_id": room_id,
        "recruiter": current_user.username,
        "message_count": len(messages),
        "messages": messages
    }