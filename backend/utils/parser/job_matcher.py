from typing import List, Dict
import re
from database.mongo import get_job_collection
from models.job import Job

async def find_matching_jobs(resume_skills: List[str], job_title: str = None, job_description: str = None) -> List[Dict]:
    """
    Find jobs from MongoDB that match the candidate's skills and preferences.
    
    Args:
        resume_skills: List of skills extracted from the resume
        job_title: Optional job title to boost matching
        job_description: Optional job description to boost matching
    
    Returns:
        List of top 3 matching jobs with match percentages
    """
    job_collection = get_job_collection()
    
    # Get all active jobs
    jobs = await job_collection.find({"status": "active"}).to_list(length=None)
    matches = []
    
    for job in jobs:
        # Convert job skills to lowercase for case-insensitive matching
        job_skills = [skill.lower() for skill in job.get("skills_required", [])]
        resume_skills_lower = [skill.lower() for skill in resume_skills]
        
        # Calculate basic skill match percentage
        matching_skills = set(resume_skills_lower) & set(job_skills)
        if not job_skills:  # Avoid division by zero
            continue
            
        base_score = len(matching_skills) / len(job_skills) * 100
        
        # Initialize final score with base skill match
        final_score = base_score
        
        # Title match bonus (up to 15%)
        if job_title:
            job_title_lower = job_title.lower()
            if job_title_lower in job["title"].lower():
                final_score += 15
            elif any(word in job["title"].lower() for word in job_title_lower.split()):
                final_score += 5
        
        # Skills importance weighting
        critical_skills_bonus = 0
        if "skills_required" in job:
            critical_skills = set(skill.lower() for skill in job["skills_required"][:3])  # Top 3 skills are considered critical
            critical_matches = critical_skills & set(resume_skills_lower)
            critical_skills_bonus = (len(critical_matches) / len(critical_skills)) * 10
        final_score += critical_skills_bonus
        
        # Experience level match (if available)
        experience_bonus = 0
        if "experience_level" in job and job_description:
            exp_level = job["experience_level"].lower()
            if exp_level in job_description.lower():
                experience_bonus = 5
        final_score += experience_bonus
        
        # Cap the final score at 100
        final_score = min(final_score, 100)
        
        matches.append({
            "job_id": str(job["_id"]),
            "title": job["title"],
            "company_name": job["company_name"],
            "location": job["location"],
            "match_percent": round(final_score, 1),
            "matching_skills": list(matching_skills),
            "missing_skills": list(set(job_skills) - set(resume_skills_lower))
        })
    
    # Sort by match percentage and return top 3
    return sorted(matches, key=lambda x: x["match_percent"], reverse=True)[:3]

def calculate_skill_match_details(resume_skills: List[str], job_skills: List[str]) -> Dict:
    """
    Calculate detailed skill match information between resume and job skills.
    
    Args:
        resume_skills: List of skills from the resume
        job_skills: List of required skills from the job
    
    Returns:
        Dictionary containing match details
    """
    resume_skills_lower = [skill.lower() for skill in resume_skills]
    job_skills_lower = [skill.lower() for skill in job_skills]
    
    matching_skills = set(resume_skills_lower) & set(job_skills_lower)
    missing_skills = set(job_skills_lower) - set(resume_skills_lower)
    extra_skills = set(resume_skills_lower) - set(job_skills_lower)
    
    match_percent = (len(matching_skills) / len(job_skills_lower) * 100) if job_skills_lower else 0
    
    return {
        "match_percent": round(match_percent, 1),
        "matching_skills": list(matching_skills),
        "missing_skills": list(missing_skills),
        "extra_skills": list(extra_skills),
        "total_required_skills": len(job_skills_lower),
        "total_matching_skills": len(matching_skills)
    }
