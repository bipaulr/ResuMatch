from typing import List
from fastapi import Depends, HTTPException, status
from .auth_utils import get_current_user
from models.user import User

async def get_current_student(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependency to check if the current user is a student.
    Raises 403 if not a student.
    """
    if current_user.role != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Student role required."
        )
    return current_user

async def get_current_recruiter(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependency to check if the current user is a recruiter.
    Raises 403 if not a recruiter.
    """
    if current_user.role != "recruiter":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Recruiter role required."
        )
    return current_user

async def validate_roles(current_user: User = Depends(get_current_user), allowed_roles: List[str] = None) -> User:
    """
    Generic role validation dependency.
    
    Args:
        current_user: The authenticated user
        allowed_roles: List of roles allowed to access the endpoint
    """
    if allowed_roles is None:
        return current_user
        
    if current_user.role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied. Required roles: {', '.join(allowed_roles)}"
        )
    return current_user
