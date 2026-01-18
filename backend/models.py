"""
NutriSnap Backend - Pydantic Models
Defines the MongoDB schema and API request/response models.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from bson import ObjectId


class PyObjectId(ObjectId):
    """Custom ObjectId type for Pydantic validation."""

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, _):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type="string")


# ==================== Database Models ====================


class NutritionData(BaseModel):
    """Nutritional macro breakdown."""

    calories: float = Field(..., description="Total calories", ge=0)
    protein: float = Field(..., description="Protein in grams", ge=0)
    carbs: float = Field(..., description="Carbohydrates in grams", ge=0)
    fats: float = Field(..., description="Fats in grams", ge=0)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "calories": 450.0,
                "protein": 25.0,
                "carbs": 50.0,
                "fats": 15.0,
            }
        }
    )


class UserProfile(BaseModel):
    """User configuration and health profile."""

    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    username: str = Field(..., min_length=3, max_length=50)
    daily_calorie_goal: int = Field(..., description="Target calories per day", gt=0)
    health_goal: str = Field(
        ...,
        description="User's health objective",
        pattern="^(gain_muscle|lose_weight|maintain|bulk|cut)$",
    )
    height_cm: Optional[float] = Field(None, description="Height in centimeters", gt=0)
    weight_kg: Optional[float] = Field(None, description="Weight in kilograms", gt=0)

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "username": "ali_tunis",
                "daily_calorie_goal": 2500,
                "health_goal": "gain_muscle",
                "height_cm": 175.0,
                "weight_kg": 70.0,
            }
        },
    )


class MealLog(BaseModel):
    """Record of a logged meal with AI analysis."""

    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    user_id: PyObjectId = Field(..., description="Reference to user")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    dish_name: str = Field(..., description="User-verified dish name")
    image_url: Optional[str] = Field(None, description="Stored image path/URL")
    nutrition: NutritionData
    ai_advice: str = Field(..., description="Personalized dietary advice from Advisor Agent")

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "user_id": "507f1f77bcf86cd799439011",
                "dish_name": "Bowl of Lablabi with tuna and egg, approx 400g",
                "nutrition": {
                    "calories": 450.0,
                    "protein": 25.0,
                    "carbs": 50.0,
                    "fats": 15.0,
                },
                "ai_advice": "Great protein choice! For dinner, focus on lean chicken with vegetables to stay within your 2500 calorie goal.",
            }
        },
    )


# ==================== API Request Models ====================


class AnalyzeImageRequest(BaseModel):
    """Request for image analysis (Vision Agent)."""

    # File upload will be handled via FastAPI's UploadFile
    # This model is for any additional metadata
    user_id: Optional[str] = Field(None, description="Optional user ID for context")


class LogMealRequest(BaseModel):
    """Request to log a verified meal."""

    user_id: str = Field(..., description="User ID (ObjectId as string)")
    verified_text: str = Field(
        ...,
        min_length=3,
        description="User-verified dish description from Vision Agent",
    )
    image_url: Optional[str] = Field(None, description="Optional stored image URL")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "user_id": "507f1f77bcf86cd799439011",
                "verified_text": "Hlalem soup with chickpeas, 350ml",
            }
        }
    )


# ==================== API Response Models ====================


class AnalyzeImageResponse(BaseModel):
    """Response from Vision Agent analysis."""

    detected_text: str = Field(..., description="AI-generated dish description")
    confidence: Optional[str] = Field(None, description="Confidence level if applicable")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "detected_text": "Bowl of Lablabi with tuna and egg, approx 400g"
            }
        }
    )


class LogMealResponse(BaseModel):
    """Response after successfully logging a meal."""

    meal_id: str = Field(..., description="Created meal log ID")
    dish_name: str
    nutrition: NutritionData
    ai_advice: str
    timestamp: datetime

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "meal_id": "507f191e810c19729de860ea",
                "dish_name": "Hlalem soup with chickpeas, 350ml",
                "nutrition": {
                    "calories": 320.0,
                    "protein": 18.0,
                    "carbs": 45.0,
                    "fats": 8.0,
                },
                "ai_advice": "Excellent fiber choice! Pair with lean protein for dinner.",
                "timestamp": "2026-01-18T17:30:00Z",
            }
        }
    )


class DashboardResponse(BaseModel):
    """User's daily dashboard summary."""

    user_id: str
    daily_goal: int
    total_consumed: float = Field(..., description="Total calories consumed today")
    remaining: float = Field(..., description="Remaining calories for the day")
    meals_today: int = Field(..., description="Number of meals logged today")
    nutrition_totals: NutritionData

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "user_id": "507f1f77bcf86cd799439011",
                "daily_goal": 2500,
                "total_consumed": 1450.0,
                "remaining": 1050.0,
                "meals_today": 3,
                "nutrition_totals": {
                    "calories": 1450.0,
                    "protein": 80.0,
                    "carbs": 160.0,
                    "fats": 45.0,
                },
            }
        }
    )
