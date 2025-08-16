import os
from typing import Optional
from fastapi import HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from dotenv import load_dotenv

# Import JWT handler and models
from .jwt_handler import oauth2_scheme, verify_token, TokenData
from models.user import User
from database.mongo import users_collection

# Load environment variables
load_dotenv()

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """
    Hashes a plain-text password using bcrypt.

    Args:
        password (str): The plain-text password to hash.

    Returns:
        str: The hashed password.
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain-text password against a hashed password.

    Args:
        plain_password (str): The plain-text password provided by the user.
        hashed_password (str): The hashed password stored in the database.

    Returns:
        bool: True if the passwords match, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """
    Get the current authenticated user from JWT token.
    
    Args:
        token (str): JWT token from Authorization header
        
    Returns:
        User: The authenticated user
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Verify the token
        token_data = verify_token(token, token_type="access")
        
        if token_data is None or token_data.username is None:
            raise credentials_exception

        # Get user from database
        db_user = await users_collection.find_one({"username": token_data.username})
        
        if db_user is None:
            raise credentials_exception

        # Create User model instance
        current_user = User(
            username=db_user["username"],
            email=db_user.get("email", ""),
            password=db_user["password"],  # Note: This should be hashed
            role=db_user["role"],
        )
        
        return current_user
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in get_current_user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during user authentication.",
        )

async def get_user_by_username(username: str) -> Optional[dict]:
    """
    Get user from database by username or email.
    
    Args:
        username (str): The username or email to search for
        
    Returns:
        Optional[dict]: User document if found, None otherwise
    """
    # Try to find by username first
    user = await users_collection.find_one({"username": username})
    
    # If not found, try to find by email
    if user is None:
        user = await users_collection.find_one({"email": username})
    
    return user

async def authenticate_user(username: str, password: str) -> Optional[User]:
    """
    Authenticate a user with username and password.
    
    Args:
        username (str): The username
        password (str): The plain text password
        
    Returns:
        Optional[User]: User object if authentication successful, None otherwise
    """
    db_user = await get_user_by_username(username)
    
    if db_user is None:
        return None
    
    if not verify_password(password, db_user["password"]):
        return None
    
    return User(
        username=db_user["username"],
        email=db_user.get("email", ""),
        password=db_user["password"],
        role=db_user["role"]
    )