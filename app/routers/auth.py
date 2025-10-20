from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone
from app.services.auth_service import AuthService
from app.middleware.auth_middleware import get_current_user
from app.models.user import User
from typing import Optional

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Request/Response Models
class GoogleCredentialRequest(BaseModel):
    credential: str

class UserProfileUpdateRequest(BaseModel):
    username: Optional[str] = None
    selected_avatar: Optional[str] = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict

class UserResponse(BaseModel):
    success: bool
    user: dict
    message: str = "User retrieved successfully"

@router.post("/google", response_model=TokenResponse)
async def authenticate_with_google(google_cred: GoogleCredentialRequest):
    """
    Authenticate user with Google OAuth
    
    This endpoint:
    1. Verifies the Google credential token
    2. Creates new user or updates existing user
    3. Returns JWT token for ClashSaga API
    """
    try:
        user, access_token = await AuthService.authenticate_with_google(google_cred.credential)
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=user.to_dict()
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Authentication failed: {str(e)}"
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user information
    
    Requires: Valid JWT token in Authorization header
    """
    # Update last seen
    current_user.last_seen = datetime.now(timezone.utc)
    await current_user.save()
    
    return UserResponse(
        success=True,
        user=current_user.to_dict()
    )

@router.put("/profile", response_model=UserResponse)
async def update_user_profile(
    profile_data: UserProfileUpdateRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Update user profile (username and avatar selection)
    
    This is called after login when user selects username and avatar
    from the popup mentioned in BRD
    """
    try:
        updated_user = await AuthService.update_user_profile(
            str(current_user.id),
            profile_data.username,
            profile_data.selected_avatar
        )
        
        return UserResponse(
            success=True,
            user=updated_user.to_dict(),
            message="Profile updated successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Profile update failed: {str(e)}"
        )

@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """
    Logout user (mainly for updating last_seen)
    
    Note: JWT tokens are stateless, so actual logout happens on client side
    by removing the token from storage
    """
    current_user.last_seen = datetime.now(timezone.utc)
    await current_user.save()
    
    return {"success": True, "message": "Logged out successfully"}

@router.get("/validate")
async def validate_token(current_user: User = Depends(get_current_user)):
    """
    Validate if current token is valid
    
    Used by frontend to check token validity
    """
    return {
        "success": True, 
        "valid": True, 
        "user_id": str(current_user.id),
        "message": "Token is valid"
    }
