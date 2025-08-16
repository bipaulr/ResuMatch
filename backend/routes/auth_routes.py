from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from database.mongo import users_collection
from auth.auth_utils import (
    hash_password, verify_password, get_current_user, authenticate_user
)
from auth.jwt_handler import create_token_pair, refresh_access_token, Token
from models.user import User

router = APIRouter()

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    role: str  # "student" or "recruiter"

class UserLogin(BaseModel):
    username: str
    password: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str

@router.post("/signup", response_model=dict)
async def signup(user: UserCreate):
    """
    Register a new user (student or recruiter).
    """
    # Validate role
    if user.role.lower() not in ["student", "recruiter"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Role must be 'student' or 'recruiter'"
        )
    
    # Check if user already exists
    existing_user = await users_collection.find_one({"username": user.username})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Username already registered"
        )
    
    # Check if email already exists
    existing_email = await users_collection.find_one({"email": user.email})
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Email already registered"
        )
    
    # Hash password and create user
    hashed_password = hash_password(user.password)
    user_doc = {
        "username": user.username,
        "email": user.email,
        "password": hashed_password,
        "role": user.role.lower()
    }
    
    result = await users_collection.insert_one(user_doc)
    
    if result.inserted_id:
        return {
            "message": "User created successfully",
            "username": user.username,
            "role": user.role.lower()
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Login user and return JWT tokens.
    """
    # Authenticate user
    user = await authenticate_user(form_data.username, form_data.password)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create token pair
    token_pair = create_token_pair(user.username, user.email, user.role)
    
    return token_pair

@router.post("/login-json", response_model=Token)
async def login_json(user_login: UserLogin):
    """
    Alternative login endpoint that accepts JSON instead of form data.
    """
    # Authenticate user
    user = await authenticate_user(user_login.username, user_login.password)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    # Create token pair
    token_pair = create_token_pair(user.username, user.email, user.role)
    
    return token_pair

@router.post("/refresh", response_model=dict)
async def refresh_token(refresh_request: RefreshTokenRequest):
    """
    Refresh access token using refresh token.
    """
    # Extract username from refresh token
    from ..auth.jwt_handler import verify_token
    token_data = verify_token(refresh_request.refresh_token, token_type="refresh")
    
    if token_data is None or token_data.username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    # Get user from database to get current role
    db_user = await users_collection.find_one({"username": token_data.username})
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    # Generate new access token
    new_access_token = refresh_access_token(refresh_request.refresh_token, db_user["role"])
    
    if new_access_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    return {
        "access_token": new_access_token,
        "token_type": "bearer"
    }

@router.get("/me", response_model=dict)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current user information.
    """
    return {
        "username": current_user.username,
        "email": current_user.email,
        "role": current_user.role
    }

@router.post("/logout")
async def logout():
    """
    Logout user (client should discard tokens).
    """
    # In a stateless JWT system, logout is typically handled on the client side
    # by discarding the tokens. For additional security, you could implement
    # a token blacklist using the revoke_token function from jwt_handler.py
    return {"message": "Successfully logged out"}

@router.get("/protected")
async def protected_route(current_user: User = Depends(get_current_user)):
    """
    Example protected route that requires authentication.
    """
    return {
        "message": f"Hello {current_user.username}! You are a {current_user.role}.",
        "user": {
            "username": current_user.username,
            "email": current_user.email,
            "role": current_user.role
        }
    }