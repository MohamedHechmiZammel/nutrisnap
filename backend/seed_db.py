"""
Database Seeding Script for NutriSnap
Creates test user for development and testing.
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()


async def seed_database():
    """Create a test user in MongoDB."""
    
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    database_name = os.getenv("DATABASE_NAME", "nutrisnap_db")
    
    client = AsyncIOMotorClient(mongo_uri)
    db = client[database_name]
    users_collection = db["users"]
    
    # Check if test user already exists
    existing_user = await users_collection.find_one({"username": "test_user"})
    
    if existing_user:
        print(f"[OK] Test user already exists with ID: {existing_user['_id']}")
        print(f"\n[INFO] Use this user_id for API testing: {existing_user['_id']}")
        return
    
    # Create test user
    test_user = {
        "username": "test_user",
        "daily_calorie_goal": 2500,
        "health_goal": "gain_muscle",
        "height_cm": 175.0,
        "weight_kg": 70.0,
    }
    
    result = await users_collection.insert_one(test_user)
    
    print(f"[OK] Created test user with ID: {result.inserted_id}")
    print(f"\n[INFO] User Profile:")
    print(f"   Username: test_user")
    print(f"   Goal: Gain Muscle")
    print(f"   Daily Calorie Target: 2500")
    print(f"\n[KEY] Use this user_id for API testing: {result.inserted_id}")

    
    client.close()


if __name__ == "__main__":
    asyncio.run(seed_database())
