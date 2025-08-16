import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "7"))

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Validate JWT configuration
if not SECRET_KEY:
    raise ValueError("JWT_SECRET environment variable not set. Please check your .env file.")

class TokenData(BaseModel):
    """Model for token data validation"""
    username: Optional[str] = None
    role: Optional[str] = None

class Token(BaseModel):
    """Model for token response"""
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: int

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data (Dict[str, Any]): The data to encode in the token (e.g., {"sub": username, "role": role})
        expires_delta (Optional[timedelta]): Optional expiration time override
        
    Returns:
        str: Encoded JWT access token
    """
    to_encode = data.copy()
    
    # Set expiration time
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Add standard JWT claims
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })
    
    # Encode the JWT
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT refresh token.
    
    Args:
        data (Dict[str, Any]): The data to encode in the token
        expires_delta (Optional[timedelta]): Optional expiration time override
        
    Returns:
        str: Encoded JWT refresh token
    """
    to_encode = data.copy()
    
    # Set expiration time (longer for refresh tokens)
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    # Add standard JWT claims
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"
    })
    
    # Encode the JWT
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_token_pair(username: str, email: str, role: str) -> Token:
    """
    Create both access and refresh tokens for a user.
    
    Args:
        username (str): The username to encode in the token
        email (str): The user email to encode in the token
        role (str): The user role to encode in the token
        
    Returns:
        Token: Token pair with access token, refresh token, and metadata
    """
    # Common token data
    token_data = {
        "sub": username,
        "email": email,
        "username": username,
        "role": role
    }
    
    # Create tokens
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token({"sub": username})  # Refresh tokens typically contain minimal data
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60  # Convert to seconds
    )

def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode and validate a JWT token.
    
    Args:
        token (str): The JWT token to decode
        
    Returns:
        Optional[Dict[str, Any]]: Decoded payload if valid, None otherwise
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

def verify_token(token: str, token_type: str = "access") -> Optional[TokenData]:
    """
    Verify a JWT token and extract token data.
    
    Args:
        token (str): The JWT token to verify
        token_type (str): Expected token type ("access" or "refresh")
        
    Returns:
        Optional[TokenData]: Token data if valid, None otherwise
    """
    payload = decode_token(token)
    
    if payload is None:
        return None
    
    # Verify token type
    if payload.get("type") != token_type:
        return None
    
    # Extract token data
    username = payload.get("sub")
    role = payload.get("role")
    
    if username is None:
        return None
    
    return TokenData(username=username, role=role)

def refresh_access_token(refresh_token: str, user_role: str) -> Optional[str]:
    """
    Create a new access token from a valid refresh token.
    
    Args:
        refresh_token (str): The refresh token
        user_role (str): The user's role (needed for new access token)
        
    Returns:
        Optional[str]: New access token if refresh token is valid, None otherwise
    """
    token_data = verify_token(refresh_token, token_type="refresh")
    
    if token_data is None or token_data.username is None:
        return None
    
    # Create new access token
    new_token_data = {
        "sub": token_data.username,
        "role": user_role
    }
    
    return create_access_token(new_token_data)

def get_token_expiration(token: str) -> Optional[datetime]:
    """
    Get the expiration time of a JWT token.
    
    Args:
        token (str): The JWT token
        
    Returns:
        Optional[datetime]: Expiration time if token is valid, None otherwise
    """
    payload = decode_token(token)
    
    if payload is None:
        return None
    
    exp_timestamp = payload.get("exp")
    if exp_timestamp is None:
        return None
    
    return datetime.fromtimestamp(exp_timestamp)

def is_token_expired(token: str) -> bool:
    """
    Check if a JWT token is expired.
    
    Args:
        token (str): The JWT token to check
        
    Returns:
        bool: True if expired or invalid, False if still valid
    """
    expiration = get_token_expiration(token)
    
    if expiration is None:
        return True
    
    return datetime.utcnow() > expiration

def revoke_token(token: str) -> bool:
    """
    Revoke a JWT token (placeholder implementation).
    
    In a production environment, you would store revoked tokens in a blacklist
    (Redis, database, etc.) and check against it during token validation.
    
    Args:
        token (str): The token to revoke
        
    Returns:
        bool: True if successfully revoked
    """
    # TODO: Implement token blacklisting in production
    # This could involve storing the token JTI (JWT ID) in a blacklist
    # For now, this is a placeholder that always returns True
    return True

def create_password_reset_token(username: str, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a special JWT token for password reset purposes.
    
    Args:
        username (str): The username for password reset
        expires_delta (Optional[timedelta]): Optional expiration time (default: 15 minutes)
        
    Returns:
        str: Encoded JWT token for password reset
    """
    if expires_delta is None:
        expires_delta = timedelta(minutes=15)  # Short expiration for security
    
    expire = datetime.utcnow() + expires_delta
    
    to_encode = {
        "sub": username,
        "type": "password_reset",
        "exp": expire,
        "iat": datetime.utcnow()
    }
    
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_password_reset_token(token: str) -> Optional[str]:
    """
    Verify a password reset token and return the username.
    
    Args:
        token (str): The password reset token
        
    Returns:
        Optional[str]: Username if token is valid, None otherwise
    """
    payload = decode_token(token)
    
    if payload is None:
        return None
    
    # Verify token type
    if payload.get("type") != "password_reset":
        return None
    
    return payload.get("sub")
