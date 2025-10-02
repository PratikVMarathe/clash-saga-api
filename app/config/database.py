from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.config.settings import settings
from app.models.user import User
# from app.models.room import Room
# from app.models.game import Game
import logging

class DatabaseManager:
    client: AsyncIOMotorClient = None
    database = None

db_manager = DatabaseManager()

async def connect_to_mongo():
    """Create database connection"""
    try:
        db_manager.client = AsyncIOMotorClient(settings.mongodb_url)
        db_manager.database = db_manager.client[settings.database_name]
        
        # Initialize Beanie with document models
        await init_beanie(
            database=db_manager.database,
            document_models=[User]
        )
        
        logging.info("Successfully connected to MongoDB Atlas")
        
    except Exception as e:
        logging.error(f"Error connecting to MongoDB: {e}")
        raise

async def close_mongo_connection():
    """Close database connection"""
    if db_manager.client:
        db_manager.client.close()
        logging.info("Disconnected from MongoDB Atlas")

async def get_database():
    """Get database instance"""
    return db_manager.database
