# Calorify

A personal fitness tracking web app built with Django. Log your food and workouts, get AI-powered meal and exercise recommendations, and stay motivated with a built-in RPG progression system.

## Features

- **Food Diary** — Search and log meals using the Edamam food database. Tracks calories, macronutrients (protein, carbs, fat), and 30+ micronutrients per day.
- **Exercise Tracking** — Search and log strength exercises with sets, reps, and weight.
- **AI Recommendations** — Ask ChatGPT to analyze your history, generate a personalized meal plan, or create a weekly exercise schedule based on your goals.
- **RPG System** — Earn XP and gems by completing daily, weekly, and monthly fitness challenges.
- **Progress Charts** — Visualize your calorie intake history on the home dashboard.
- **User Profiles** — Stores height, weight, body fat, activity level, and goals to personalize TDEE and calorie targets.

## Tech Stack

- **Backend:** Django 4, SQLite
- **Frontend:** HTMX, Tailwind CSS
- **AI:** OpenAI GPT-3.5 / GPT-4
- **Food Data:** Edamam Food Database API
- **Exercise Data:** MuscleWiki via RapidAPI

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js (for Tailwind CSS compilation)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repo-url>
   cd Calorify
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # macOS/Linux
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**

   Copy the example below into a `.env` file at the project root and fill in your API keys:
   ```
   DJANGO_SECRET_KEY=your-secret-key-here

   EDAMAM_FOOD_DB_KEY=your-edamam-food-key
   EDAMAM_RECIPE_DB_KEY=your-edamam-recipe-key
   EDAMAM_NUTRIENTS_ANALYSIS_KEY=your-edamam-nutrients-key

   OPEN_AI_KEY=your-openai-key
   RAPID_API_KEY=your-rapidapi-key
   ```

   API keys can be obtained from:
   - [Edamam](https://developer.edamam.com/) — Food Database, Recipe Search, and Nutrition Analysis APIs
   - [OpenAI](https://platform.openai.com/) — ChatGPT access
   - [RapidAPI / MuscleWiki](https://rapidapi.com/musclewiki/api/musclewiki/) — Exercise database

5. **Run database migrations**
   ```bash
   python manage.py migrate
   ```

6. **Start the development server**
   ```bash
   python manage.py runserver
   ```

   The app will be available at `http://127.0.0.1:8000`.

### Tailwind CSS (optional, for frontend changes)

```bash
cd app/jstoolchain
npm install
npm run build
```

## Project Structure

```
Calorify/
├── app/
│   ├── models.py        # All data models (User, Food, DailyEntry, Challenge, etc.)
│   ├── views.py         # Request handlers
│   ├── api.py           # Edamam and OpenAI API integration
│   ├── forms.py         # Django forms
│   ├── urls.py          # App URL routes
│   ├── templates/       # HTML templates
│   ├── static/          # JS and CSS
│   └── scripts/
│       └── credentials.py  # Loads API keys from .env
├── calorify/
│   ├── settings.py
│   └── urls.py
├── .env                 # Your local secrets (never committed)
└── requirements.txt
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `DJANGO_SECRET_KEY` | Django secret key for cryptographic signing |
| `EDAMAM_FOOD_DB_KEY` | Edamam Food Database API key |
| `EDAMAM_RECIPE_DB_KEY` | Edamam Recipe Database API key |
| `EDAMAM_NUTRIENTS_ANALYSIS_KEY` | Edamam Nutrition Analysis API key |
| `OPEN_AI_KEY` | OpenAI API key for GPT meal/exercise recommendations |
| `RAPID_API_KEY` | RapidAPI key for the MuscleWiki exercise database |
