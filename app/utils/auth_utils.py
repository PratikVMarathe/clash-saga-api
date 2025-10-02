import os
import jwt
from datetime import datetime, timedelta, timezone
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from fastapi import HTTPException, status
from app.config.settings import settings
from typing import Optional

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_access_token_expire_minutes)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "access"
    })
    
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.jwt_secret_key, 
        algorithm=settings.jwt_algorithm
    )
    return encoded_jwt

def verify_token(token: str) -> str:
    """Verify JWT token and return user ID"""
    try:
        payload = jwt.decode(
            token, 
            settings.jwt_secret_key, 
            algorithms=[settings.jwt_algorithm]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def verify_google_token(credential: str) -> dict:
    """Verify Google OAuth token and extract user info"""
    try:
        # Verify the token with Google
        id_info = id_token.verify_oauth2_token(
            credential, 
            google_requests.Request(), 
            settings.google_client_id
        )
        
        # Validate the issuer
        if id_info['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Wrong issuer.')
        
        # Extract user information
        user_info = {
            'google_id': id_info['sub'],
            'email': id_info.get('email'),
            'name': id_info.get('name', ''),
            'avatar': id_info.get('picture'),
            'email_verified': id_info.get('email_verified', False)
        }
        
        return {"success": True, "user_info": user_info}
        
    except ValueError as e:
        print(f"Google token verification failed: {e}")
        return {"success": False, "error": str(e)}
    except Exception as e:
        print(f"Unexpected error during Google token verification: {e}")
        return {"success": False, "error": "Token verification failed"}

def generate_username_from_email(email: str) -> str:
    """Generate a username from email"""
    return email.split('@')[0].replace('.', '_').replace('+', '_')
