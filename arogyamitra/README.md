# 🌿 ArogyaMitra – AI-Driven Workout Planning, Nutrition Guidance & Health Coaching Platform

## Overview

ArogyaMitra is a full-stack AI fitness platform built with **FastAPI** (backend) and **React** (frontend). It provides personalized workout plans, nutrition guidance, health assessments, and real-time AI coaching through AROMI — your intelligent wellness companion.

---

## 🏗️ Project Structure

```
ArogyaMitra/
├── backend/
│   ├── app/
│   │   ├── models/user.py          # SQLAlchemy DB models (User, WorkoutPlan, NutritionPlan, etc.)
│   │   ├── routers/
│   │   │   ├── auth.py             # JWT Auth: register, login, /me
│   │   │   ├── users.py            # Profile management, dashboard stats
│   │   │   ├── workouts.py         # AI workout plan generation
│   │   │   ├── nutrition.py        # AI nutrition plan generation
│   │   │   ├── progress.py         # Progress logging & analytics
│   │   │   ├── chat.py             # AROMI chat endpoint
│   │   │   ├── health_assessment.py # BMI, health score
│   │   │   └── ai_coach.py         # Dynamic plan adjustments, motivation
│   │   ├── services/
│   │   │   └── ai_agent.py         # ArogyaMitraAgent (Groq LLaMA-3.3-70B)
│   │   ├── utils/config.py         # Pydantic settings from .env
│   │   └── database.py             # SQLAlchemy engine + session
│   ├── main.py                     # FastAPI app entry point
│   ├── requirements.txt
│   └── .env.example
│
└── frontend/
    └── index.html                  # Complete React SPA (no build step needed!)
```

---

## 🚀 Quick Start

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate     # Windows
source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your API keys (especially GROQ_API_KEY)

# Start server
python main.py
# → http://localhost:8000
# → Swagger docs: http://localhost:8000/docs
```

### Frontend Setup

```bash
# Simply open frontend/index.html in a browser, OR serve it:
cd frontend
npx serve .
# → http://localhost:3000
```

---

## 🔑 API Keys Required

| Service | Key | Where to get |
|---------|-----|--------------|
| **Groq** (AI Core) | `GROQ_API_KEY` | https://console.groq.com/keys |
| **YouTube** | `YOUTUBE_API_KEY` | https://console.cloud.google.com |
| **Spoonacular** | `SPOONACULAR_API_KEY` | https://spoonacular.com/food-api/console |
| **Google Calendar** | OAuth credentials | https://console.cloud.google.com |

---

## 🎯 Features

### Epic 1: Environment Setup ✅
- Python virtual environment
- Project folder structure (backend/frontend)
- .env configuration
- Dependency management

### Epic 2: Backend API (FastAPI) ✅
- **JWT Authentication** — Register, login, token-based auth
- **Modular Routers** — auth, users, workouts, nutrition, progress, chat, health, ai_coach
- **Database Models** — User, WorkoutPlan, NutritionPlan, ProgressRecord, HealthAssessment, ChatSession
- **Service Layer** — AI agent, business logic separated from routing

### Epic 3: AI Integration ✅
- **Groq LLaMA-3.3-70B** — Core AI for plan generation and AROMI chat
- **Personalized Workout Plans** — 7-day AI-generated programs
- **Nutrition Plans** — Calorie-optimized, diet-preference-aware meal plans
- **AROMI Coach** — Context-aware conversational wellness AI
- **Progress Analysis** — AI-powered insights from user data
- **Dynamic Adjustments** — Plans adapt to travel, injury, busy schedules

### Epic 4: React Frontend ✅
- **Dashboard** — Stats overview, AI motivation, quick actions
- **Workout Module** — Day-by-day exercise viewer with sets/reps
- **Nutrition Module** — Meal cards with macro breakdowns & pie charts
- **Progress Tracker** — Logging + recharts visualizations + AI analysis
- **AROMI Chat** — Full-featured conversational AI interface
- **Health Assessment** — BMI calculator, health score, recommendations
- **Profile Management** — Edit all user preferences

### Epic 5: Architecture ✅
- SQLite database (easily upgradeable to PostgreSQL)
- Environment-based configuration
- CORS middleware for frontend-backend communication
- Pydantic validation on all endpoints

---

## 🛠️ Technology Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI, SQLAlchemy, Pydantic, Uvicorn |
| Database | SQLite (dev) / PostgreSQL (prod) |
| AI | Groq LLaMA-3.3-70B Versatile |
| Auth | JWT (python-jose), bcrypt |
| Frontend | React 18, Recharts, vanilla CSS |
| Fonts | Syne (display) + Space Grotesk (body) |

---

## 📡 API Endpoints

```
POST   /api/auth/register          Register new user
POST   /api/auth/login             Login (returns JWT)
GET    /api/auth/me                Get current user

GET    /api/users/profile          Get user profile
PUT    /api/users/profile          Update profile
GET    /api/users/dashboard-stats  Dashboard statistics

POST   /api/workouts/generate      Generate AI workout plan
GET    /api/workouts/current       Get active plan
GET    /api/workouts/history       Plan history

POST   /api/nutrition/generate     Generate AI nutrition plan
GET    /api/nutrition/current      Active nutrition plan

POST   /api/progress/log           Log daily progress
GET    /api/progress/history       Progress records
GET    /api/progress/analytics     AI-powered analytics

POST   /api/chat/aromi             Chat with AROMI AI
GET    /api/chat/history           Chat history

POST   /api/health/assess          Health assessment
GET    /api/health/latest          Latest assessment

POST   /api/ai-coach/aromi-chat    Advanced AI coaching
POST   /api/ai-coach/adjust-plan   Dynamic plan adjustment
GET    /api/ai-coach/motivate      Daily motivation
```

---

## 💡 Notes

- The frontend is a self-contained HTML file — no build step required
- Works without API keys (fallback responses provided)
- With Groq API key, full AI features unlock
- Database auto-creates on first run (SQLite)
