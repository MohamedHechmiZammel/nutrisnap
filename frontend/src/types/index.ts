export interface NutritionData {
    calories: number;
    protein: number;
    carbs: number;
    fats: number;
}

export interface MealLog {
    meal_id: string;
    dish_name: string;
    nutrition: NutritionData;
    ai_advice: string;
    timestamp: string;
}

export interface AnalyzeImageResponse {
    detected_text: string;
}

export interface LogMealRequest {
    user_id: string;
    verified_text: string;
    image_url?: string;
}

export interface DashboardResponse {
    user_id: string;
    daily_goal: number;
    total_consumed: number;
    remaining: number;
    meals_today: number;
    nutrition_totals: NutritionData;
}
