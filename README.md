# NutriSnap - AI-Powered Meal Tracking Application

**Tunisian Market MVP** using "The AI Council" architecture.

## Architecture Overview

NutriSnap uses a chain of specialized AI agents orchestrated by LangChain:

1. **Vision Agent** (Google Gemini 1.5 Flash): Identifies dishes and ingredients from photos
2. **Human-in-the-Loop**: User verification and editing of AI detection
3. **Nutrition Agent** (CalorieNinjas API): Quantifies macronutrients
4. **Advisor Agent** (Groq/Llama 3): Provides personalized dietary advice

## Tech Stack

- **Backend**: Python 3.10+ with FastAPI
- **Frontend**: React Native (Expo) with TypeScript
- **Database**: MongoDB (Local Instance)
- **AI Orchestration**: LangChain
- **External APIs**: Gemini, CalorieNinjas, Groq

## Project Structure

```
galactic-pioneer/
├── backend/
│   ├── main.py              # FastAPI app entry point
│   ├── database.py          # MongoDB async connection
│   ├── models.py            # Pydantic schemas
│   ├── services/
│   │   └── ai_council.py    # AI agent orchestration
│   └── requirements.txt
├── frontend/                # React Native (Expo) app
└── .env                     # Environment variables (not committed)
```

## Setup Instructions

### Prerequisites

1. **Python 3.10+** installed
2. **MongoDB** running locally on `mongodb://localhost:27017`
3. **Node.js 18+** (for frontend, Phase 4)

### Backend Setup

1. **Clone and navigate to the project**:
   ```bash
   cd c:\Users\MPSHOP\.gemini\antigravity\playground\galactic-pioneer
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r backend\requirements.txt
   ```

4. **Configure environment variables**:
   - Copy `.env.example` to `.env`
   - Add your API keys:
     - `GOOGLE_API_KEY` (from Google AI Studio)
     - `GROQ_API_KEY` (from Groq Console)
     - `CALORIENINJAS_API_KEY` (from CalorieNinjas)
     - `MONGO_URI` (default: `mongodb://localhost:27017`)

5. **Start MongoDB**:
   ```bash
   # Ensure MongoDB service is running
   mongod
   ```

6. **Run the backend server**:
   ```bash
   uvicorn backend.main:app --reload
   ```

7. **Verify**: Navigate to `http://localhost:8000/health`

## API Workflow

### 1. Image Upload → Vision Extraction
```
POST /analyze
- User uploads meal image
- Gemini identifies dish and estimates portion
- Returns text description
```

### 2. Human Verification
```
Frontend displays AI guess
User edits text if needed
User confirms
```

### 3. Nutrition Quantification + Advice
```
POST /log-meal
- Backend sends verified text to CalorieNinjas
- Sums macronutrients from returned items
- Advisor Agent generates dietary advice
- Saves meal log to MongoDB
```

### 4. Dashboard
```
GET /dashboard/{user_id}
- Returns daily totals vs calorie goal
- Shows meal history
```

## Development Guidelines

- **Type Safety**: All Python functions use type hints
- **PEP8 Compliance**: Follow Python style guidelines
- **No Hardcoded Secrets**: Always use environment variables
- **Error Handling**: Every external API call has try/except
- **Semantic Commits**: Use `feat:`, `fix:`, `chore:` prefixes

## License

MIT License - Tunisian Market MVP
