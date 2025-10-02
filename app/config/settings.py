from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # Application
    app_name: str = "ClashSaga API"
    debug: bool = True
    version: str = "1.0.0"
    environment: str = "development"
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Database
    mongodb_url: str
    database_name: str = "clashsaga"
    
    # Google OAuth
    google_client_id: str
    google_client_secret: str
    
    # JWT
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 1440
    
    # CORS
    allowed_origins: List[str] = ["http://localhost:3000"]
    
    # WebSocket
    ws_max_connections: int = 1000
    ws_ping_interval: int = 20
    ws_ping_timeout: int = 10
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Create settings instance
settings = Settings()
