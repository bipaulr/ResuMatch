from bson import ObjectId
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, Query
from fastapi.responses import JSONResponse, FileResponse
from typing import List, Optional
from datetime import datetime
from auth.dependencies import get_current_student
from utils.parser.resume_parser import extract_text_from_pdf, clean_text, extract_fields
from utils.parser.gemini_client import pdf_to_text, get_gemini_response, get_gemini_mock_interview_response, get_gemini_interview_question, get_mock_interview_questions_for_analysis, generate_interview_feedback
from utils.parser.job_matcher import find_matching_jobs, calculate_skill_match_details
from models.job import Job
from models.user import User
import os
import json
from database.mongo import get_job_collection, get_database, get_resumes_collection, get_users_collection


router = APIRouter()

REPORTS_DIR = "reports"
os.makedirs(REPORTS_DIR, exist_ok=True)

@router.get("/stats")
async def get_student_stats(current_user: User = Depends(get_current_student)):
    """
    Get student dashboard statistics.
    """
    try:
        db = get_database()
        applications_collection = db.applications
        resumes_collection = get_resumes_collection()
        
        # Count applications for this student
        application_count = await applications_collection.count_documents({
            "student_id": current_user.username
        })
        
        # Find latest resume for this student
        latest_resume = await resumes_collection.find_one(
            {"student_id": current_user.username}, sort=[("uploaded_at", -1)]
        )
        has_resume = latest_resume is not None

        # Extract real values if present
        resume_score = None
        job_matches = 0
        if latest_resume:
            # Prefer 'score' if computed during upload; fallback to analysis score
            resume_score = latest_resume.get("score")
            if resume_score is None:
                analysis = latest_resume.get("analysis") or {}
                gem = analysis.get("gemini_analysis") or {}
                resume_score = gem.get("resume_quality_score")
            # Matching jobs stored during upload
            matching_jobs = latest_resume.get("matching_jobs") or []
            job_matches = len(matching_jobs)

        return {
            "resume_score": resume_score if has_resume else None,
            "job_matches": job_matches if has_resume else 0,
            "applications": application_count,
            "recent_activity": [
                {
                    "id": "1",
                    "type": "application",
                    "title": "Applied to a position",
                    "timestamp": datetime.utcnow().isoformat()
                }
            ]
        }
    except Exception as e:
        print(f"Error getting student stats: {e}")
        # Return default stats on error
        return {
            "resume_score": None,
            "job_matches": 0,
            "applications": 0,
            "recent_activity": []
        }

@router.post("/mock-interview")
async def mock_interview(
    role: str = Form(...),
    job_description: Optional[str] = Form(None),
    current_user: User = Depends(get_current_student)
):
    """Generate a mock interview based on the latest resume and desired role/description."""
    try:
        resumes = get_resumes_collection()
        latest = await resumes.find_one({"student_id": current_user.username}, sort=[("uploaded_at", -1)])
        if not latest:
            raise HTTPException(status_code=404, detail="Please upload a resume first.")

        resume_text = latest.get("extracted_text") or latest.get("raw_text") or ""
        if not resume_text:
            raise HTTPException(status_code=400, detail="Resume text not available for analysis.")

        desc = job_description or f"Interview for role: {role}"
        result = await get_gemini_mock_interview_response(resume_text, desc)
        return {"role": role, "result": result}
    except HTTPException:
        raise
    except Exception as e:
        print("Error in mock_interview:", e)
        raise HTTPException(status_code=500, detail="Failed to generate mock interview")

@router.post("/mock-interview/start")
async def start_mock_interview(
    role: str = Form(...),
    job_description: Optional[str] = Form(None),
    current_user: User = Depends(get_current_student)
):
    """Start a continuous mock interview session."""
    try:
        resumes = get_resumes_collection()
        latest = await resumes.find_one({"student_id": current_user.username}, sort=[("uploaded_at", -1)])
        if not latest:
            raise HTTPException(status_code=404, detail="Please upload a resume first.")

        resume_text = latest.get("extracted_text") or latest.get("raw_text") or ""
        if not resume_text:
            raise HTTPException(status_code=400, detail="Resume text not available for analysis.")

        # Create interview session
        db = get_database()
        sessions_collection = db.interview_sessions
        
        session_id = str(ObjectId())
        session_doc = {
            "_id": ObjectId(session_id),
            "student_id": current_user.username,
            "role": role,
            "job_description": job_description,
            "resume_text": resume_text,
            "created_at": datetime.utcnow(),
            "status": "active",
            "messages": []
        }
        
        await sessions_collection.insert_one(session_doc)
        
        # Generate first question
        first_question = await get_gemini_interview_question(resume_text, role, job_description, [])
        
        # Add first question to session
        await sessions_collection.update_one(
            {"_id": ObjectId(session_id)},
            {"$push": {"messages": {
                "type": "question",
                "content": first_question,
                "timestamp": datetime.utcnow()
            }}}
        )
        
        return {
            "session_id": session_id,
            "first_question": first_question,
            "status": "started"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start interview session: {str(e)}")

@router.post("/mock-interview/{session_id}/respond")
async def respond_to_interview(
    session_id: str,
    answer: str = Form(...),
    current_user: User = Depends(get_current_student)
):
    """Respond to an interview question and get the next question."""
    try:
        db = get_database()
        sessions_collection = db.interview_sessions
        
        # Find session
        session = await sessions_collection.find_one({
            "_id": ObjectId(session_id),
            "student_id": current_user.username,
            "status": "active"
        })
        
        if not session:
            raise HTTPException(status_code=404, detail="Interview session not found or ended.")
        
        # Add student's answer to session
        await sessions_collection.update_one(
            {"_id": ObjectId(session_id)},
            {"$push": {"messages": {
                "type": "answer",
                "content": answer,
                "timestamp": datetime.utcnow()
            }}}
        )
        
        # Check if student wants to end
        if answer.lower().strip() in ['stop', 'end', 'quit', 'finish', 'done', 'thank you']:
            # Generate detailed feedback before completing the interview
            conversation_history = session.get("messages", [])
            
            # Generate comprehensive feedback
            feedback = await generate_interview_feedback(
                session["resume_text"],
                session["role"],
                session.get("job_description", ""),
                conversation_history + [{"type": "answer", "content": answer}]
            )
            
            # Update session with completion status and feedback
            await sessions_collection.update_one(
                {"_id": ObjectId(session_id)},
                {
                    "$set": {
                        "status": "completed", 
                        "ended_at": datetime.utcnow(),
                        "feedback": feedback
                    }
                }
            )
            
            return {
                "status": "completed",
                "message": "Thank you for practicing with us! Your mock interview session has been completed. Check out your detailed feedback below.",
                "is_complete": True,
                "feedback": feedback
            }
        
        # Generate next question based on conversation history
        conversation_history = session.get("messages", [])
        next_question = await get_gemini_interview_question(
            session["resume_text"], 
            session["role"], 
            session.get("job_description"), 
            conversation_history + [{"type": "answer", "content": answer}]
        )
        
        # Add next question to session (the interview continues until user stops)
        await sessions_collection.update_one(
            {"_id": ObjectId(session_id)},
            {"$push": {"messages": {
                "type": "question",
                "content": next_question,
                "timestamp": datetime.utcnow()
            }}}
        )
        
        return {
            "next_question": next_question,
            "status": "active",
            "is_complete": False
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process response: {str(e)}")

@router.get("/mock-interview/{session_id}")
async def get_interview_session(
    session_id: str,
    current_user: User = Depends(get_current_student)
):
    """Get interview session details."""
    try:
        db = get_database()
        sessions_collection = db.interview_sessions
        
        session = await sessions_collection.find_one({
            "_id": ObjectId(session_id),
            "student_id": current_user.username
        })
        
        if not session:
            raise HTTPException(status_code=404, detail="Interview session not found.")
        
        # Convert ObjectId to string
        session["_id"] = str(session["_id"])
        return session
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get session: {str(e)}")

@router.get("/mock-interview/{session_id}/feedback")
async def get_interview_feedback(
    session_id: str,
    current_user: User = Depends(get_current_student)
):
    """Get detailed feedback for a completed interview session."""
    try:
        db = get_database()
        sessions_collection = db.interview_sessions
        
        session = await sessions_collection.find_one({
            "_id": ObjectId(session_id),
            "student_id": current_user.username,
            "status": "completed"
        })
        
        if not session:
            raise HTTPException(status_code=404, detail="Completed interview session not found.")
        
        # Return feedback if available
        feedback = session.get("feedback")
        if not feedback:
            # Generate feedback if not already available
            conversation_history = session.get("messages", [])
            feedback = await generate_interview_feedback(
                session["resume_text"],
                session["role"],
                session.get("job_description", ""),
                conversation_history
            )
            
            # Save the generated feedback
            await sessions_collection.update_one(
                {"_id": ObjectId(session_id)},
                {"$set": {"feedback": feedback}}
            )
        
        return {
            "session_id": session_id,
            "role": session["role"],
            "completed_at": session.get("ended_at"),
            "feedback": feedback
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get feedback: {str(e)}")

@router.get("/resume-analysis")
async def get_resume_analysis(current_user: User = Depends(get_current_student)):
    """
    Get the latest resume analysis for the current student.
    """
    try:
        resumes = get_resumes_collection()
        doc = await resumes.find_one({"student_id": current_user.username}, sort=[("uploaded_at", -1)])
        if not doc or not doc.get("analysis"):
            raise HTTPException(status_code=404, detail="No resume analysis found")
        return doc["analysis"]
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting resume analysis: {e}")
        raise HTTPException(status_code=500, detail="Failed to get resume analysis")

@router.get("/job-recommendations")
async def get_job_recommendations(current_user: User = Depends(get_current_student)):
    """
    Get job recommendations based on student's skills and preferences.
    """
    try:
        job_collection = get_job_collection()

        # Get up to 10 active jobs as recommendations
        # In real implementation, this would be based on student's skills
        cursor = (
            job_collection.find({"status": "active"})
            .sort("created_at", -1)
            .limit(10)
        )

        jobs = []
        async for job in cursor:
            job["id"] = str(job.pop("_id"))
            jobs.append(Job(**job))

        return jobs
    except Exception as e:
        print(f"Error getting job recommendations: {e}")
        return []

@router.get("/applications")
async def get_student_applications(current_user: User = Depends(get_current_student)):
    """
    Get all applications submitted by the current student.
    """
    try:
        db = get_database()
        applications_collection = db.applications
        job_collection = get_job_collection()
        
        # Get all applications for this student
        cursor = applications_collection.find({
            "student_id": current_user.username
        }).sort("applied_at", -1)
        
        applications = []
        async for app in cursor:
            # Get job details
            job = await job_collection.find_one({"_id": ObjectId(app["job_id"])})
            if job:
                job["id"] = str(job.pop("_id"))
                applications.append({
                    "id": str(app["_id"]),
                    "job": Job(**job),
                    "status": app.get("status", "pending"),
                    "applied_at": app["applied_at"].isoformat()
                })
                
        return applications
    except Exception as e:
        print(f"Error getting applications: {e}")
        return []

@router.post("/apply/{job_id}")
async def apply_to_job_alt(
    job_id: str,
    current_user: User = Depends(get_current_student)
):
    """
    Alternative endpoint for applying to a job (redirects to main apply endpoint).
    """
    # This is the same as the /jobs/{job_id}/apply endpoint
    return await apply_to_job(job_id, current_user)

def extract_skills_from_job_description(job_description: str, job_title: str) -> List[str]:
    """
    Extract potential skills from job description text.
    This is a simple implementation - could be enhanced with NLP.
    """
    # Common tech skills to look for
    tech_keywords = [
        'python', 'java', 'javascript', 'react', 'node.js', 'sql', 'mongodb', 
        'aws', 'docker', 'kubernetes', 'git', 'agile', 'scrum', 'api', 'rest',
        'html', 'css', 'typescript', 'angular', 'vue', 'express', 'fastapi',
        'postgresql', 'mysql', 'redis', 'machine learning', 'ai', 'data science',
        'tensorflow', 'pytorch', 'pandas', 'numpy', 'flask', 'django'
    ]
    
    job_text = (job_description + " " + job_title).lower()
    found_skills = []
    
    for skill in tech_keywords:
        if skill in job_text:
            found_skills.append(skill)
    
    return found_skills


# Job listing routes
@router.get("/jobs", response_model=List[Job])
async def list_jobs(
    current_user: User = Depends(get_current_student),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    location: Optional[str] = None,
    company: Optional[str] = None,
    skills: Optional[List[str]] = Query(None)
):
    """
    Get a list of all active jobs with optional filtering.
    """
    job_collection = get_job_collection()
    
    # Build the query filter
    query = {"status": "active"}
    if location:
        query["location"] = {"$regex": location, "$options": "i"}
    if company:
        query["company_name"] = {"$regex": company, "$options": "i"}
    if skills:
        query["skills_required"] = {"$all": skills}
        
    # Execute the query with pagination
    cursor = job_collection.find(query) \
        .sort("created_at", -1) \
        .skip(skip) \
        .limit(limit)
        
    jobs = []
    async for job in cursor:
        job["id"] = str(job.pop("_id"))  # Convert ObjectId to string
        jobs.append(Job(**job))
        
    return jobs

@router.get("/jobs/{job_id}", response_model=Job)
async def get_job_details(
    job_id: str,
    current_user: User = Depends(get_current_student)
):
    """
    Get detailed information about a specific job.
    """
    job_collection = get_job_collection()
    job = await job_collection.find_one({"_id": ObjectId(job_id)})
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    job["id"] = str(job.pop("_id"))
    return Job(**job)

@router.post("/jobs/{job_id}/apply")
async def apply_to_job(
    job_id: str,
    current_user: User = Depends(get_current_student)
):
    """
    Apply to a specific job and create a chat room.
    """
    job_collection = get_job_collection()
    db = get_database()
    applications_collection = db.applications
    chat_rooms_collection = db.chat_rooms
    
    # Check if job exists and is active
    job = await job_collection.find_one({"_id": ObjectId(job_id)})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.get("status") != "active":
        raise HTTPException(status_code=400, detail="This job is no longer accepting applications")
        
    # Check if already applied
    existing_application = await applications_collection.find_one({
        "job_id": job_id,
        "student_id": current_user.username
    })
    
    if existing_application:
        raise HTTPException(status_code=400, detail="You have already applied to this job")
        
    # Record the application
    application = {
        "job_id": job_id,
        "student_id": current_user.username,
        "student_email": current_user.email,
        "recruiter_id": job["recruiter_id"],
        "company_name": job["company_name"],
        "job_title": job["title"],
        "status": "pending",
        "applied_at": datetime.utcnow()
    }
    
    result = await applications_collection.insert_one(application)
    
    if not result.inserted_id:
        raise HTTPException(status_code=500, detail="Failed to submit application")
    
    # Create a chat room for the student and recruiter
    chat_room = {
        "job_id": job_id,
        "student_id": current_user.username,
        "recruiter_id": job["recruiter_id"],
        "created_at": datetime.utcnow(),
        "last_message_at": datetime.utcnow(),
        "is_active": True
    }
    
    # Check if chat room already exists
    existing_room = await chat_rooms_collection.find_one({
        "job_id": job_id,
        "student_id": current_user.username,
        "recruiter_id": job["recruiter_id"]
    })
    
    chat_room_id = None
    if not existing_room:
        chat_result = await chat_rooms_collection.insert_one(chat_room)
        chat_room_id = str(chat_result.inserted_id)
    else:
        chat_room_id = str(existing_room["_id"])
        
    return {
        "message": "Application submitted successfully",
        "application_id": str(result.inserted_id),
        "job_title": job["title"],
        "company_name": job["company_name"],
        "chat_room_id": chat_room_id
    }

@router.get("/chat-rooms")
async def get_student_chat_rooms(current_user: User = Depends(get_current_student)):
    """Get all chat rooms for the current student."""
    db = get_database()
    chat_rooms_collection = db.chat_rooms
    messages_collection = db.messages
    job_collection = get_job_collection()
    
    # Find all chat rooms where the student is a participant
    rooms = await chat_rooms_collection.find({
        "student_id": current_user.username,
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
        
        # Count unread messages for this student
        unread_count = await messages_collection.count_documents({
            "room_id": room_id,
            "receiver_id": current_user.username,
            "read": False
        })
        
        enriched_room = {
            "id": room_id,
            "job_id": room["job_id"],
            "recruiter_id": room["recruiter_id"],
            "job_title": job["title"] if job else "Unknown Job",
            "company_name": job["company_name"] if job else "Unknown Company",
            "created_at": room["created_at"].isoformat(),
            "last_message": {
                "content": last_message["content"] if last_message else None,
                "sender_id": last_message["sender_id"] if last_message else None,
                "timestamp": last_message["timestamp"].isoformat() if last_message else None
            } if last_message else None,
            "unread_count": unread_count,
            "participants": [current_user.username, room["recruiter_id"]]
        }
        enriched_rooms.append(enriched_room)
    
    return {"chat_rooms": enriched_rooms}
    

@router.post("/analyze-resume")
async def analyze_resume(
    file: UploadFile = File(...),
    company_name: str = Form(...),
    job_title: str = Form(...),
    job_description: str = Form(...),
    current_user: User = Depends(get_current_student)
):
    if not file.filename.lower().endswith(".pdf"):
        return JSONResponse(content={"error": "Only PDF files are allowed."}, status_code=400)
    try:
        pdf_bytes = await file.read()
        resume_text = pdf_to_text(pdf_bytes)
        print("Extracted Resume Text:\n", resume_text)
        cleaned_text = clean_text(resume_text)
        print("Cleaned Resume Text:\n", cleaned_text)
        skill_fields = extract_fields(cleaned_text)
        print("Extracted Skill Fields:", skill_fields)
        input_prompt = f"""
        Resume Text: {cleaned_text}

        Company Name: {company_name}
        Job Title: {job_title}
        Job Description: {job_description}

        Skill Fields: {', '.join(skill_fields)}

        Tasks:
        1. List missing keywords for job matching.
        2. Provide a profile summary.
        3. Return a resume quality score (0-100).
        4. Return scores for tone & style, content, and structure (0-100 each).
        5. Calculate percentage match for the job description.
        6. Suggest top 3 job roles based on skills.
        7. Analyze keyword optimization for ATS (Applicant Tracking System).
        8. Provide an overall ATS resume score (0-100).
        9. Suggest specific improvements to increase the ATS resume score, focusing on keyword usage, formatting, and relevance.
        Respond in JSON format with keys: missing_keywords, profile_summary, resume_quality_score, tone_style_score, content_score, structure_score, percentage_match, top_job_suggestions, keyword_optimization, ats_resume_score, ats_improvement_suggestions.
        """
        print("Prompt sent to Gemini:\n", input_prompt)
        response = await get_gemini_response(cleaned_text, job_description, skill_fields)
        print("Raw Gemini Response:\n", response)
        top_jobs = await find_matching_jobs(skill_fields, job_title, job_description)
        print("Top Job Suggestions:", top_jobs)

        # Calculate detailed skill match for the specific job
        extracted_job_skills = extract_skills_from_job_description(job_description, job_title)
        skill_match_details = calculate_skill_match_details(skill_fields, extracted_job_skills)
        print("Extracted Job Skills:", extracted_job_skills)
        print("Skill Match Details:", skill_match_details)

        # Parse scores from Gemini response with better error handling
        gemini_json = {}
        try:
            # Try to parse as JSON first
            if response.strip().startswith('{'):
                gemini_json = json.loads(response)
            else:
                # If it's not JSON, try to extract JSON from the response
                import re
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    gemini_json = json.loads(json_match.group())
                else:
                    # Fallback: create a structured response from text
                    gemini_json = {
                        "missing_keywords": [],
                        "profile_summary": response[:500] + "..." if len(response) > 500 else response,
                        "resume_quality_score": 75,
                        "tone_style_score": 70,
                        "content_score": 80,
                        "structure_score": 75,
                        "percentage_match": skill_match_details["match_percent"],
                        "top_job_suggestions": [job["title"] for job in top_jobs],
                        "keyword_optimization": "Please review the full response for details",
                        "ats_resume_score": 70,
                        "ats_improvement_suggestions": ["Optimize keywords", "Improve formatting"]
                    }
            print("Parsed Gemini JSON:", gemini_json)
        except Exception as e:
            print("Error parsing Gemini response:", e)
            # Provide fallback values with actual skill match data
            gemini_json = {
                "missing_keywords": skill_match_details["missing_skills"],
                "profile_summary": "Analysis completed with skill matching",
                "resume_quality_score": 75,
                "tone_style_score": 70,
                "content_score": 80,
                "structure_score": 75,
                "percentage_match": skill_match_details["match_percent"],
                "top_job_suggestions": [job["title"] for job in top_jobs],
                "keyword_optimization": f"Found {len(skill_match_details['matching_skills'])} matching skills",
                "ats_resume_score": max(50, int(skill_match_details["match_percent"])),
                "ats_improvement_suggestions": [f"Add skills: {', '.join(skill_match_details['missing_skills'][:3])}"]
            }

        def score_color(score):
            try:
                score = int(score)
            except Exception:
                return "grey"
            if score >= 80:
                return "green"
            elif score >= 50:
                return "yellow"
            else:
                return "red"

        # Get scores and colors
        resume_quality_score = gemini_json.get("resume_quality_score", 0)
        tone_style_score = gemini_json.get("tone_style_score", 0)
        content_score = gemini_json.get("content_score", 0)
        structure_score = gemini_json.get("structure_score", 0)
        print("Scores:", resume_quality_score, tone_style_score, content_score, structure_score)

        scores = {
            "resume_quality_score": {
                "value": resume_quality_score,
                "color": score_color(resume_quality_score)
            },
            "tone_style_score": {
                "value": tone_style_score,
                "color": score_color(tone_style_score)
            },
            "content_score": {
                "value": content_score,
                "color": score_color(content_score)
            },
            "structure_score": {
                "value": structure_score,
                "color": score_color(structure_score)
            }
        }
        print("Score Colors:", scores)

        # Generate mock interview questions for the resume analysis
        print("Generating mock interview questions...")
        mock_questions = await get_mock_interview_questions_for_analysis(cleaned_text, job_description or job_title or "General position")
        print("Generated Mock Interview Questions:", mock_questions)

        report_data = {
            "gemini_analysis": gemini_json,
            "extracted_skills": skill_fields,
            "top_job_suggestions": top_jobs,
            "skill_match_details": skill_match_details,
            "scores": scores,
            "mock_interview_questions": mock_questions
        }
        print("Final Report Data:", report_data)
        # Save report to file
        report_path = os.path.join(REPORTS_DIR, f"{file.filename}_report.json")
        try:
            with open(report_path, "w") as f:
                json.dump(report_data, f, indent=2)
            print("Report saved at:", report_path)
        except Exception as e:
            print("Error saving report:", e)

        # Persist analysis to the latest uploaded resume for this student
        try:
            resumes = get_resumes_collection()
            latest_resume = await resumes.find_one(
                {"student_id": current_user.username}, sort=[("uploaded_at", -1)]
            )
            if latest_resume:
                await resumes.update_one(
                    {"_id": latest_resume["_id"]},
                    {"$set": {"analysis": report_data, "analyzed_at": datetime.utcnow()}}
                )
            else:
                # If no resume exists, create a minimal record with analysis
                await resumes.insert_one({
                    "student_id": current_user.username,
                    "filename": file.filename,
                    "file_path": None,
                    "raw_text": None,
                    "extracted_text": None,
                    "extracted_fields": [],
                    "uploaded_at": datetime.utcnow(),
                    "analysis": report_data,
                    "analyzed_at": datetime.utcnow()
                })
        except Exception as e:
            print("Error persisting resume analysis:", e)
        return {
            **report_data,
            "download_report_url": f"/download-report?filename={file.filename}_report.json"
        }
    except Exception as e:
        print("Error in analyze_resume:", e)
        return JSONResponse(content={"error": str(e)}, status_code=500)

@router.post("/upload-resume")
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_student)
):
    if not file.filename.lower().endswith(".pdf"):
        return JSONResponse(content={"detail": "Only PDF files are allowed."}, status_code=400)
    try:
        contents = await file.read()
        raw_text = extract_text_from_pdf(contents)
        if not raw_text:
            return JSONResponse(content={"detail": "Failed to parse resume."}, status_code=500)
        cleaned_text = clean_text(raw_text)
        fields = extract_fields(cleaned_text)

        # Save file to disk for now
        uploads_dir = os.path.join("uploads", "resumes")
        os.makedirs(uploads_dir, exist_ok=True)
        saved_path = os.path.join(uploads_dir, f"{current_user.username}_{file.filename}")
        with open(saved_path, "wb") as f:
            f.write(contents)

        # Compute a simple score and suggestions
        def compute_score(text: str, fields: List[str]) -> int:
            base = min(60 + len(fields) * 3, 95)
            length_bonus = min(len(text) // 2000, 5)
            return min(base + length_bonus, 100)

        score = compute_score(cleaned_text, fields)

        # Suggested edits: encourage missing common items
        suggested_edits = []
        if len(cleaned_text) < 1000:
            suggested_edits.append("Expand experience details with measurable impact.")
        if not any(k in [f.lower() for f in fields] for k in ["leadership", "communication", "teamwork"]):
            suggested_edits.append("Add soft skills (leadership, communication, teamwork) where relevant.")
        if not any(k in [f.lower() for f in fields] for k in ["python", "javascript", "sql"]):
            suggested_edits.append("Highlight core technical stacks explicitly (e.g., Python, JavaScript, SQL).")

        # Match jobs based on extracted skills
        try:
            matching_jobs = await find_matching_jobs(fields)
        except Exception as _:
            matching_jobs = []

        # Store in MongoDB
        resumes = get_resumes_collection()
        doc = {
            "student_id": current_user.username,
            "filename": file.filename,
            "file_path": saved_path,
            "raw_text": raw_text,
            "extracted_text": cleaned_text,
            "extracted_fields": fields,
            "uploaded_at": datetime.utcnow(),
            # Store quick analysis
            "score": score,
            "suggested_edits": suggested_edits,
            "matching_jobs": matching_jobs,
            "analysis": None
        }
        await resumes.insert_one(doc)

        # Update user record with resume flag
        try:
            users = get_users_collection()
            await users.update_one(
                {"username": current_user.username},
                {"$set": {"resume_uploaded": True}}
            )
        except Exception as _:
            pass

        return {
            "message": "Resume uploaded",
            "filename": file.filename,
            "resume_uploaded": True,
            "raw_text": raw_text,
            "extracted_text": cleaned_text,
            "extracted_fields": fields,
            "score": score,
            "suggested_edits": suggested_edits,
            "matching_jobs": matching_jobs,
        }
    except Exception as e:
        print("Error in upload_resume:", e)
        return JSONResponse(content={"detail": str(e)}, status_code=500)

@router.get("/download-report")
async def download_report(filename: str):
    file_path = os.path.join(REPORTS_DIR, filename)
    if not os.path.exists(file_path):
        return JSONResponse(content={"error": "Report not found"}, status_code=404)
    return FileResponse(file_path, media_type="application/json", filename=filename)

@router.post("/improve-resume")
async def improve_resume(file: UploadFile = File(...), job_description: str = Form(...)):
    if not file.filename.lower().endswith(".pdf"):
        return JSONResponse(content={"error": "Only PDF files are allowed."}, status_code=400)
    try:
        pdf_bytes = await file.read()
        resume_text = pdf_to_text(pdf_bytes)
        input_prompt = """
        You are an experienced HR with Tech Experience in all fields there is in the job market.
        Your task is to review the provided resume against job description.
        Please share professional evaluation on the candidate's profile and alignment with the job description.
        Highlight strengths and weaknesses in relation to the job requirements.
        """
        response = await get_gemini_response(resume_text, job_description, [])
        return {"result": response}
    except Exception as e:
        print("Error in improve_resume:", e)
        return JSONResponse(content={"error": str(e)}, status_code=500)

@router.post("/missing-keywords")
async def missing_keywords(file: UploadFile = File(...), job_description: str = Form(...)):
    if not file.filename.lower().endswith(".pdf"):
        return JSONResponse(content={"error": "Only PDF files are allowed."}, status_code=400)
    try:
        pdf_bytes = await file.read()
        resume_text = pdf_to_text(pdf_bytes)
        input_prompt = """
        Analyze the resume and job description. Identify keywords and skills from the job description that are missing in the resume.
        Prioritize based on frequency and relevance. Suggest how to integrate these keywords into the resume using measurable, achievement-based phrasing.
        """
        response = await get_gemini_response(resume_text, job_description, [])
        return {"result": response}
    except Exception as e:
        print("Error in missing_keywords:", e)
        return JSONResponse(content={"error": str(e)}, status_code=500)

@router.post("/percentage-match")
async def percentage_match(file: UploadFile = File(...), job_description: str = Form(...)):
    if not file.filename.lower().endswith(".pdf"):
        return JSONResponse(content={"error": "Only PDF files are allowed."}, status_code=400)
    try:
        pdf_bytes = await file.read()
        resume_text = pdf_to_text(pdf_bytes)
        input_prompt = """
        Analyze the resume and job description. Score the resume's match as a percentage (0–100%) based on skill, experience, and keyword alignment.
        Justify the score briefly with strengths and gaps.
        """
        response = await get_gemini_response(resume_text, job_description, [])
        return {"result": response}
    except Exception as e:
        print("Error in percentage_match:", e)
        return JSONResponse(content={"error": str(e)}, status_code=500)