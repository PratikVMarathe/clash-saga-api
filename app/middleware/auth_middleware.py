from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.utils.auth_utils import verify_token
from app.models.user import User
from typing import Optional

class JWTBearer(HTTPBearer):
    """JWT Bearer token authentication"""
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Invalid authentication scheme."
                )
            if not self.verify_jwt(credentials.credentials):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Invalid token or expired token."
                )
            return credentials.credentials
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid authorization code."
            )

    def verify_jwt(self, jwt_token: str) -> bool:
        """Verify if JWT token is valid"""
        try:
            verify_token(jwt_token)
            return True
        except:
            return False

# Dependency to get current user
async def get_current_user(token: str = Depends(JWTBearer())) -> User:
    """Get current authenticated user"""
    user_id = verify_token(token)
    user = await User.get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return user

# Optional authentication (for public endpoints that can use auth)
async def get_current_user_optional(
    authorization: Optional[str] = Depends(JWTBearer(auto_error=False))
) -> Optional[User]:
    """Get current user if authenticated, None otherwise"""
    if not authorization:
        return None
    try:
        user_id = verify_token(authorization)
        user = await User.get(user_id)
        if user and user.is_active:
            return user
    except:
        pass
    return None
