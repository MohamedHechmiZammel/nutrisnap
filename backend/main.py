"""
NutriSnap Backend - FastAPI Application
AI-Powered Meal Tracking Application using "The AI Council" Architecture.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import connect_to_mongo, close_mongo_connection


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event handler for startup and shutdown.
    Manages MongoDB connection lifecycle.
    """
    # Startup
    print("🚀 NutriSnap Backend Starting...")
    await connect_to_mongo()
    yield
    # Shutdown
    print("🛑 NutriSnap Backend Shutting Down...")
    await close_mongo_connection()


# Initialize FastAPI app
app = FastAPI(
    title="NutriSnap API",
    description="AI-Powered Meal Tracking for the Tunisian Market",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS Configuration (for React Native frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== Health Check ====================


@app.get("/health", tags=["System"])
async def health_check():
    """
    Health check endpoint to verify the server is running.

    Returns:
        dict: Server status and version.
    """
    return {
        "status": "healthy",
        "service": "NutriSnap Backend",
        "version": "1.0.0",
    }




# ==================== Phase 3 Endpoints ====================

from datetime import datetime, timedelta
from typing import Optional
from fastapi import UploadFile, File, HTTPException, Depends
from bson import ObjectId

from models import (
    AnalyzeImageResponse,
    LogMealRequest,
    LogMealResponse,
    DashboardResponse,
    NutritionData,
    MealLog,
)
from database import get_users_collection, get_meal_logs_collection
from services.ai_council import get_ai_council, AICouncil


@app.post("/analyze", response_model=AnalyzeImageResponse, tags=["AI Council"])
async def analyze_image(
    image: UploadFile = File(..., description="Meal image (JPEG/PNG)")
):
    """
    Vision Agent endpoint: Analyze meal image and return AI-generated description.

    The user will verify/edit this text before final submission via /log-meal.

    Args:
        image: Uploaded image file.

    Returns:
        AnalyzeImageResponse: Detected dish description.

    Raises:
        HTTPException: If image processing or Vision Agent fails.
    """
    try:
        # Validate file type
        if not image.content_type.startswith("image/"):
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Only images (JPEG/PNG) are supported.",
            )

        # Read image bytes
        image_bytes = await image.read()

        if len(image_bytes) > 10 * 1024 * 1024:  # 10MB limit
            raise HTTPException(status_code=400, detail="Image too large (max 10MB).")

        # Get AI Council and analyze
        council = get_ai_council()
        detected_text = await council.analyze_image(image_bytes)

        return AnalyzeImageResponse(detected_text=detected_text)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Image analysis failed: {str(e)}"
        )


@app.post("/log-meal", response_model=LogMealResponse, tags=["Meal Tracking"])
async def log_meal(request: LogMealRequest):
    """
    Meal logging endpoint: Process verified text, calculate nutrition, generate advice, save to DB.

    Workflow:
    1. Fetch user profile from MongoDB
    2. Calculate current daily total
    3. Call Nutrition + Advisor agents
    4. Save meal log to database

    Args:
        request: LogMealRequest with user_id and verified_text.

    Returns:
        LogMealResponse: Complete meal log with nutrition and advice.

    Raises:
        HTTPException: If user not found or any AI agent fails.
    """
    try:
        users_collection = get_users_collection()
        meal_logs_collection = get_meal_logs_collection()

        # Convert user_id string to ObjectId
        try:
            user_object_id = ObjectId(request.user_id)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid user_id format.")

        # Fetch user profile
        user = await users_collection.find_one({"_id": user_object_id})
        if not user:
            raise HTTPException(status_code=404, detail="User not found.")

        # Calculate current daily total (sum of today's meals)
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_meals = meal_logs_collection.find(
            {"user_id": user_object_id, "timestamp": {"$gte": today_start}}
        )

        current_daily_total = 0.0
        async for meal in today_meals:
            current_daily_total += meal.get("nutrition", {}).get("calories", 0)

        # Process meal through AI Council
        council = get_ai_council()
        result = await council.process_meal(
            verified_text=request.verified_text,
            user_profile={
                "health_goal": user.get("health_goal", "maintain"),
                "daily_calorie_goal": user.get("daily_calorie_goal", 2500),
            },
            current_daily_total=current_daily_total,
        )

        # Create meal log document
        meal_log = {
            "user_id": user_object_id,
            "timestamp": datetime.utcnow(),
            "dish_name": request.verified_text,
            "image_url": request.image_url,
            "nutrition": result["nutrition"],
            "ai_advice": result["ai_advice"],
        }

        # Insert into MongoDB
        insert_result = await meal_logs_collection.insert_one(meal_log)

        # Return response
        return LogMealResponse(
            meal_id=str(insert_result.inserted_id),
            dish_name=request.verified_text,
            nutrition=NutritionData(**result["nutrition"]),
            ai_advice=result["ai_advice"],
            timestamp=meal_log["timestamp"],
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Meal logging failed: {str(e)}")


@app.get("/dashboard/{user_id}", response_model=DashboardResponse, tags=["Dashboard"])
async def get_dashboard(user_id: str):
    """
    User dashboard endpoint: Return daily totals vs calorie goal.

    Aggregates all meals from today and calculates:
    - Total calories consumed
    - Remaining calories
    - Number of meals
    - Macro totals

    Args:
        user_id: User's ObjectId as string.

    Returns:
        DashboardResponse: Daily summary with nutrition totals.

    Raises:
        HTTPException: If user not found.
    """
    try:
        users_collection = get_users_collection()
        meal_logs_collection = get_meal_logs_collection()

        # Convert user_id string to ObjectId
        try:
            user_object_id = ObjectId(user_id)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid user_id format.")

        # Fetch user profile
        user = await users_collection.find_one({"_id": user_object_id})
        if not user:
            raise HTTPException(status_code=404, detail="User not found.")

        daily_goal = user.get("daily_calorie_goal", 2500)

        # Get today's meals
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_meals = meal_logs_collection.find(
            {"user_id": user_object_id, "timestamp": {"$gte": today_start}}
        )

        # Aggregate nutrition totals
        total_calories = 0.0
        total_protein = 0.0
        total_carbs = 0.0
        total_fats = 0.0
        meals_count = 0

        async for meal in today_meals:
            nutrition = meal.get("nutrition", {})
            total_calories += nutrition.get("calories", 0)
            total_protein += nutrition.get("protein", 0)
            total_carbs += nutrition.get("carbs", 0)
            total_fats += nutrition.get("fats", 0)
            meals_count += 1

        remaining = daily_goal - total_calories

        return DashboardResponse(
            user_id=user_id,
            daily_goal=daily_goal,
            total_consumed=round(total_calories, 1),
            remaining=round(remaining, 1),
            meals_today=meals_count,
            nutrition_totals=NutritionData(
                calories=round(total_calories, 1),
                protein=round(total_protein, 1),
                carbs=round(total_carbs, 1),
                fats=round(total_fats, 1),
            ),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dashboard fetch failed: {str(e)}")



"""
Run the server with:
    uvicorn backend.main:app --reload

Access API docs at:
    http://localhost:8000/docs
"""
