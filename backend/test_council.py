"""
Quick Test Script for NutriSnap Backend
Tests the AI Council workflow end-to-end.
"""

import asyncio
import os
from dotenv import load_dotenv

load_dotenv()


async def test_ai_council():
    """Test the AI Council components individually."""
    
    print("=" * 60)
    print("NutriSnap AI Council - Quick Test")
    print("=" * 60)
    
    # Import after environment loaded
    from services.ai_council import AICouncil
    
    council = AICouncil()
    
    # Test 1: Nutrition Calculator (no image needed)
    print("\n[Test 1] Nutrition Calculator")
    print("-" * 60)
    
    test_descriptions = [
        "chickpea soup 300ml",
        "grilled chicken breast 200g with rice 150g",
        "couscous with vegetables 350g",
    ]
    
    for description in test_descriptions:
        try:
            print(f"\n[IN] Input: {description}")
            result = await council.nutrition_calculator.calculate_nutrition(description)
            print(f"[OK] Nutrition: {result}")
        except Exception as e:
            print(f"[ERROR] Error: {e}")
    
    # Test 2: Advisor Agent
    print("\n\n[Test 2] Advisor Agent")
    print("-" * 60)
    
    provider = os.getenv("ADVISOR_PROVIDER", "groq")
    print(f"Using provider: {provider}")
    
    if provider == "openrouter":
        model = os.getenv("OPENROUTER_MODEL", "unknown")
        print(f"Model: {model}")
    
    try:
        advice = await council.advisor_agent.generate_advice(
            health_goal="gain_muscle",
            dish_name="Couscous with vegetables, 350g",
            total_calories=450.0,
            remaining_calories=1050.0,
        )
        print(f"\n[OK] AI Advice: {advice}")
    except Exception as e:
        print(f"[ERROR] Error: {e}")
    
    # Test 3: Full Meal Processing
    print("\n\n[Test 3] Full Meal Processing Pipeline")
    print("-" * 60)
    
    user_profile = {
        "health_goal": "lose_weight",
        "daily_calorie_goal": 2000,
    }
    
    verified_text = "grilled fish with salad, 300g"
    current_total = 800.0
    
    try:
        print(f"[IN] Meal: {verified_text}")
        print(f"[IN] Goal: {user_profile['health_goal']}")
        print(f"[IN] Current intake: {current_total} cal")
        
        result = await council.process_meal(
            verified_text=verified_text,
            user_profile=user_profile,
            current_daily_total=current_total,
        )
        
        print(f"\n[OK] Nutrition Breakdown:")
        for key, value in result["nutrition"].items():
            print(f"   {key}: {value}")
        
        print(f"\n[OK] AI Advice: {result['ai_advice']}")
        
    except Exception as e:
        print(f"[ERROR] Error: {e}")
    
    print("\n" + "=" * 60)
    print("Testing Complete!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_ai_council())
