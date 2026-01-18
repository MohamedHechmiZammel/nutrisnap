"""
NutriSnap Backend - MongoDB Database Connection
Async connection management using Motor.
"""

import os
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Global database client
_client: Optional[AsyncIOMotorClient] = None
_database: Optional[AsyncIOMotorDatabase] = None


async def connect_to_mongo() -> None:
    """
    Initialize connection to MongoDB.
    Called during FastAPI startup.
    """
    global _client, _database

    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    database_name = os.getenv("DATABASE_NAME", "nutrisnap_db")

    try:
        _client = AsyncIOMotorClient(mongo_uri)
        _database = _client[database_name]

        # Verify connection
        await _client.admin.command("ping")
        print(f"✅ Connected to MongoDB: {database_name}")

    except Exception as e:
        print(f"❌ Failed to connect to MongoDB: {e}")
        raise


async def close_mongo_connection() -> None:
    """
    Close MongoDB connection.
    Called during FastAPI shutdown.
    """
    global _client

    if _client:
        _client.close()
        print("📴 MongoDB connection closed")


def get_database() -> AsyncIOMotorDatabase:
    """
    Get the database instance.

    Returns:
        AsyncIOMotorDatabase: The connected database instance.

    Raises:
        RuntimeError: If database is not connected.
    """
    if _database is None:
        raise RuntimeError(
            "Database not connected. Ensure connect_to_mongo() was called during startup."
        )
    return _database


# Collection accessors
def get_users_collection():
    """Get the 'users' collection."""
    db = get_database()
    return db["users"]


def get_meal_logs_collection():
    """Get the 'meal_logs' collection."""
    db = get_database()
    return db["meal_logs"]
