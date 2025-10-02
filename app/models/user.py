from beanie import Document, Indexed
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

class UserStats(BaseModel):
    """User game statistics"""
    total_games: int = 0
    games_won: int = 0
    games_lost: int = 0
    win_rate: float = 0.0
    total_playtime: int = 0  # in minutes

class User(Document):
    """User document for MongoDB"""
    # Google OAuth fields
    google_id: Indexed(str, unique=True)
    email: Indexed(EmailStr, unique=True)
    name: str
    avatar: Optional[str] = None
    
    # ClashSaga profile (set after login)
    username: Optional[str] = None
    selected_avatar: Optional[str] = None  # User's chosen avatar from popup
    
    # Account status
    is_active: bool = True
    is_verified: bool = True
    
    # Game statistics
    stats: UserStats = UserStats()
    
    # Future features
    friends: List[str] = []
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    last_seen: Optional[datetime] = None
    
    class Settings:
        collection = "users"
        
    def update_stats(self, won: bool, playtime_minutes: int):
        """Update user game statistics"""
        self.stats.total_games += 1
        if won:
            self.stats.games_won += 1
        else:
            self.stats.games_lost += 1
            
        if self.stats.total_games > 0:
            self.stats.win_rate = (self.stats.games_won / self.stats.total_games) * 100
            
        self.stats.total_playtime += playtime_minutes
        self.updated_at = datetime.utcnow()
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": str(self.id),
            "email": self.email,
            "name": self.name,
            "avatar": self.avatar,
            "username": self.username,
            "selected_avatar": self.selected_avatar,
            "stats": self.stats.dict(),
            "created_at": self.created_at.isoformat(),
            "last_login": self.last_login.isoformat() if self.last_login else None
        }