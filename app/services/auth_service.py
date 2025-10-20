from datetime import datetime, timezone
from app.models.user import User
from app.utils.auth_utils import verify_google_token, create_access_token, generate_username_from_email
from fastapi import HTTPException, status
from typing import Tuple

class AuthService:
    """Authentication service for handling user login/registration"""
    
    @staticmethod
    async def authenticate_with_google(credential: str) -> Tuple[User, str]:
        """Authenticate user with Google OAuth and return user + JWT token"""
        
        # Verify Google token
        verification_result = await verify_google_token(credential)
        
        if not verification_result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid Google credential: {verification_result.get('error', 'Unknown error')}"
            )
        
        user_info = verification_result["user_info"]
        
        # Check if email is verified
        if not user_info.get("email_verified", False):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email not verified with Google"
            )
        
        # Find existing user or create new one
        user = await User.find_one(User.google_id == user_info["google_id"])
        
        if user:
            # Update existing user's info and last login
            user.email = user_info["email"]
            user.name = user_info["name"]
            user.avatar = user_info["avatar"]
            user.last_login = datetime.now(timezone.utc)
            user.last_seen = datetime.now(timezone.utc)
            user.updated_at = datetime.now(timezone.utc)
            await user.save()
        else:
            # Create new user
            suggested_username = generate_username_from_email(user_info["email"])
            
            user = User(
                google_id=user_info["google_id"],
                email=user_info["email"],
                name=user_info["name"],
                avatar=user_info["avatar"],
                username=suggested_username,  # Can be changed later
                is_verified=True,
                last_login=datetime.now(timezone.utc),
                last_seen=datetime.now(timezone.utc)
            )
            await user.insert()
        
        # Generate JWT token
        access_token = create_access_token(data={"sub": str(user.id)})
        
        return user, access_token
    
    @staticmethod
    async def update_user_profile(user_id: str, username: str = None, selected_avatar: str = None) -> User:
        """Update user profile after login (username/avatar selection)"""
        user = await User.get(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update fields if provided
        if username:
            # Check if username is already taken
            existing_user = await User.find_one(User.username == username)
            if existing_user and str(existing_user.id) != user_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken"
                )
            user.username = username
        
        if selected_avatar:
            user.selected_avatar = selected_avatar
        
        user.updated_at = datetime.now(timezone.utc)
        await user.save()
        
        return user
    
    @staticmethod
    async def get_user_by_id(user_id: str) -> User:
        """Get user by ID"""
        user = await User.get(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user
