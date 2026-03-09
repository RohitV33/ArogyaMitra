import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import auth, users, workouts, nutrition, progress, chat, health_assessment, ai_coach, health_analysis
from app.utils.config import settings

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="ArogyaMitra API",
    description="AI-Driven Workout Planning, Nutrition Guidance, and Health Coaching Platform",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load routers
print("✅ Auth router loaded")
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
print("✅ Users router loaded")
app.include_router(users.router, prefix="/api/users", tags=["Users"])
print("✅ Workouts router loaded")
app.include_router(workouts.router, prefix="/api/workouts", tags=["Workouts"])
print("✅ Nutrition router loaded")
app.include_router(nutrition.router, prefix="/api/nutrition", tags=["Nutrition"])
print("✅ Progress router loaded")
app.include_router(progress.router, prefix="/api/progress", tags=["Progress"])
print("✅ Admin router loaded")
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
print("✅ Chat router loaded")
app.include_router(health_assessment.router, prefix="/api/health", tags=["Health Assessment"])
print("✅ Health Assessment router loaded")
app.include_router(ai_coach.router, prefix="/api/ai-coach", tags=["AROMI AI Coach"])
print("✅ AROMI AI Coach router loaded")
app.include_router(health_analysis.router, prefix="/api/health-analysis", tags=["Health Analysis AI"])

print("🌟 Starting ArogyaMitra - AI Fitness Platform")
print("👨‍💻 Mission: Transforming Lives Through AI-Powered Fitness")
print(f"🚀 Launching on: http://localhost:8000")

@app.on_event("startup")
async def startup_event():
    print("🚀 ArogyaMitra Backend Starting...")
    print("🤖 Initializing AI Agent...")
    from app.services.ai_agent import ai_agent
    print("✅ AI Agent initialized successfully!")

@app.get("/")
async def root():
    return {"message": "ArogyaMitra API - Transforming Lives Through AI-Powered Fitness", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "platform": "ArogyaMitra"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
