"""
NutriSnap AI Council - Agent Orchestration Service
LangChain-based pipeline with Vision, Nutrition, and Advisor agents.
"""

import os
import base64
from typing import Dict, List, Optional
from io import BytesIO

import httpx
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


# ==================== Vision Agent (Gemini 1.5 Flash) ====================


class VisionAgent:
    """
    Vision Agent using Google Gemini 1.5 Flash.
    Identifies Tunisian dishes and estimates portion sizes from images.
    """

    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")

        self.model = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=api_key,
            temperature=0.3,  # Lower temperature for more consistent results
        )

        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a food recognition expert specializing in Tunisian cuisine. "
                    "Identify the dish, visible ingredients, and estimate portion sizes. "
                    "Output ONLY a concise text description (e.g., 'Bowl of Lablabi with tuna and egg, approx 400g'). "
                    "Do not include explanations or additional commentary.",
                ),
                ("human", "{input}"),
            ]
        )

    async def analyze_image(self, image_bytes: bytes) -> str:
        """
        Analyze a meal image and return a text description.

        Args:
            image_bytes: Raw image data in bytes.

        Returns:
            str: Concise dish description with portion estimate.

        Raises:
            Exception: If image analysis fails.
        """
        try:
            # Convert image to base64 for Gemini API
            base64_image = base64.b64encode(image_bytes).decode("utf-8")

            # Create message with image
            message = HumanMessage(
                content=[
                    {
                        "type": "text",
                        "text": "Identify this Tunisian dish and estimate the portion size. "
                        "Provide a concise description only.",
                    },
                    {
                        "type": "image_url",
                        "image_url": f"data:image/jpeg;base64,{base64_image}",
                    },
                ]
            )

            # Invoke the model
            response = await self.model.ainvoke([message])
            detected_text = response.content.strip()

            return detected_text

        except Exception as e:
            raise Exception(f"Vision Agent failed: {str(e)}")


# ==================== Nutrition Calculator (CalorieNinjas) ====================


class NutritionCalculator:
    """
    Nutrition quantification using CalorieNinjas API.
    CRITICAL: Sums all items returned by the API.
    """

    def __init__(self):
        self.api_key = os.getenv("CALORIENINJAS_API_KEY")
        if not self.api_key:
            raise ValueError("CALORIENINJAS_API_KEY not found in environment variables")

        self.base_url = "https://api.calorieninjas.com/v1/nutrition"

    async def calculate_nutrition(self, food_description: str) -> Dict[str, float]:
        """
        Calculate nutritional values from food description.

        Args:
            food_description: Verified text description of the meal.

        Returns:
            dict: Summed macronutrients {calories, protein, carbs, fats}.

        Raises:
            Exception: If API call fails or no food items found.
        """
        try:
            async with httpx.AsyncClient() as client:
                headers = {"X-Api-Key": self.api_key}
                params = {"query": food_description}

                response = await client.get(
                    self.base_url, headers=headers, params=params, timeout=10.0
                )

                if response.status_code != 200:
                    raise Exception(
                        f"CalorieNinjas API error: {response.status_code} - {response.text}"
                    )

                data = response.json()
                items = data.get("items", [])

                if not items:
                    raise Exception(
                        "No food items recognized. Please simplify the description "
                        "(e.g., 'chickpea soup 300ml' instead of 'Hlalem')."
                    )

                # CRITICAL: Sum all items as per specification
                total_calories = sum(item.get("calories", 0) for item in items)
                total_protein = sum(item.get("protein_g", 0) for item in items)
                total_carbs = sum(
                    item.get("carbohydrates_total_g", 0) for item in items
                )
                total_fats = sum(item.get("fat_total_g", 0) for item in items)

                return {
                    "calories": round(total_calories, 1),
                    "protein": round(total_protein, 1),
                    "carbs": round(total_carbs, 1),
                    "fats": round(total_fats, 1),
                }

        except httpx.TimeoutException:
            raise Exception("CalorieNinjas API timeout. Please try again.")
        except Exception as e:
            if "No food items recognized" in str(e):
                raise
            raise Exception(f"Nutrition calculation failed: {str(e)}")


# ==================== Advisor Agent (Groq/Llama 3) ====================


class AdvisorAgent:
    """
    Strategic dietary advisor using Groq (Llama 3) or OpenRouter.
    Provides personalized advice based on user goals and remaining calories.
    """

    def __init__(self):
        # Determine which provider to use
        self.provider = os.getenv("ADVISOR_PROVIDER", "groq").lower()

        if self.provider == "openrouter":
            self.api_key = os.getenv("OPENROUTER_API_KEY")
            if not self.api_key:
                raise ValueError(
                    "OPENROUTER_API_KEY not found in environment variables"
                )
            self.model_name = os.getenv(
                "OPENROUTER_MODEL", "anthropic/claude-3.5-sonnet"
            )
            self.api_url = "https://openrouter.ai/api/v1/chat/completions"

        else:  # Default to Groq
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                raise ValueError("GROQ_API_KEY not found in environment variables")

            self.model = ChatGroq(
                groq_api_key=api_key,
                model_name="llama3-70b-8192",
                temperature=0.7,
            )

        self.prompt_template = (
            "You are a nutritionist specializing in Tunisian cuisine. "
            "Provide ONE concise sentence of specific dietary advice for the rest of the day. "
            "Be encouraging and practical.\n\n"
            "User Goal: {health_goal}\n"
            "Just ate: {dish_name} ({total_calories} calories)\n"
            "Remaining calories for today: {remaining_calories}\n"
            "Give specific advice for the rest of the day."
        )

    async def generate_advice(
        self,
        health_goal: str,
        dish_name: str,
        total_calories: float,
        remaining_calories: float,
    ) -> str:
        """
        Generate personalized dietary advice.

        Args:
            health_goal: User's health objective (e.g., 'gain_muscle', 'lose_weight').
            dish_name: Name of the meal just consumed.
            total_calories: Calories in the meal.
            remaining_calories: Remaining calories for the day.

        Returns:
            str: One sentence of specific dietary advice.

        Raises:
            Exception: If advice generation fails.
        """
        try:
            prompt = self.prompt_template.format(
                health_goal=health_goal,
                dish_name=dish_name,
                total_calories=total_calories,
                remaining_calories=remaining_calories,
            )

            if self.provider == "openrouter":
                # Use OpenRouter API directly
                advice = await self._query_openrouter(prompt)
            else:
                # Use Groq via LangChain
                advice = await self._query_groq(prompt)

            return advice.strip()

        except Exception as e:
            raise Exception(f"Advisor Agent failed: {str(e)}")

    async def _query_groq(self, prompt: str) -> str:
        """Query Groq using LangChain."""
        prompt_obj = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a nutritionist specializing in Tunisian cuisine.",
                ),
                ("human", "{input}"),
            ]
        )
        chain = prompt_obj | self.model
        response = await chain.ainvoke({"input": prompt})
        return response.content

    async def _query_openrouter(self, prompt: str) -> str:
        """Query OpenRouter API directly."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}],
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                self.api_url, headers=headers, json=payload
            )
            response.raise_for_status()

            data = response.json()
            content = data["choices"][0]["message"]["content"]
            return content



# ==================== AI Council Orchestrator ====================


class AICouncil:
    """
    Main orchestrator for the AI Council workflow.
    Coordinates Vision → Nutrition → Advisor agents.
    """

    def __init__(self):
        self.vision_agent = VisionAgent()
        self.nutrition_calculator = NutritionCalculator()
        self.advisor_agent = AdvisorAgent()

    async def analyze_image(self, image_bytes: bytes) -> str:
        """
        Step 1: Vision extraction.

        Args:
            image_bytes: Raw image data.

        Returns:
            str: AI-generated dish description.
        """
        return await self.vision_agent.analyze_image(image_bytes)

    async def process_meal(
        self,
        verified_text: str,
        user_profile: Dict,
        current_daily_total: float,
    ) -> Dict:
        """
        Steps 3-4: Nutrition quantification + strategic advice.

        Args:
            verified_text: User-verified dish description.
            user_profile: Dict with 'health_goal' and 'daily_calorie_goal'.
            current_daily_total: Calories already consumed today.

        Returns:
            dict: {
                'nutrition': {calories, protein, carbs, fats},
                'ai_advice': str
            }

        Raises:
            Exception: If any agent fails.
        """
        # Step 3: Nutrition Quantification
        nutrition = await self.nutrition_calculator.calculate_nutrition(verified_text)

        # Calculate remaining calories
        daily_goal = user_profile.get("daily_calorie_goal", 2500)
        new_total = current_daily_total + nutrition["calories"]
        remaining = daily_goal - new_total

        # Step 4: Strategic Advice
        advice = await self.advisor_agent.generate_advice(
            health_goal=user_profile.get("health_goal", "maintain"),
            dish_name=verified_text,
            total_calories=nutrition["calories"],
            remaining_calories=remaining,
        )

        return {"nutrition": nutrition, "ai_advice": advice}


# ==================== Factory Function ====================


def get_ai_council() -> AICouncil:
    """
    Factory function to create AICouncil instance.
    Use this in API endpoints to ensure proper initialization.
    """
    return AICouncil()
