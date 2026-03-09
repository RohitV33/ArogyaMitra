from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.database import get_db
from app.models.user import User, FitnessGoal, WorkoutPreference, DietPreference
from app.routers.auth import get_current_user, get_password_hash

router = APIRouter()

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    fitness_level: Optional[str] = None
    fitness_goal: Optional[FitnessGoal] = None
    workout_preference: Optional[WorkoutPreference] = None
    diet_preference: Optional[DietPreference] = None

@router.get("/profile")
async def get_profile(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "username": current_user.username,
        "full_name": current_user.full_name,
        "age": current_user.age,
        "gender": current_user.gender,
        "height": current_user.height,
        "weight": current_user.weight,
        "fitness_level": current_user.fitness_level,
        "fitness_goal": current_user.fitness_goal,
        "workout_preference": current_user.workout_preference,
        "diet_preference": current_user.diet_preference,
        "created_at": current_user.created_at
    }

@router.put("/profile")
async def update_profile(
    update_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    for field, value in update_data.dict(exclude_none=True).items():
        setattr(current_user, field, value)
    
    db.commit()
    db.refresh(current_user)
    return {"message": "Profile updated successfully!"}

@router.get("/dashboard-stats")
async def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    from app.models.user import WorkoutPlan, NutritionPlan, ProgressRecord
    
    # Get active plans
    active_workout = db.query(WorkoutPlan).filter(
        WorkoutPlan.user_id == current_user.id,
        WorkoutPlan.is_active == True
    ).first()
    
    active_nutrition = db.query(NutritionPlan).filter(
        NutritionPlan.user_id == current_user.id,
        NutritionPlan.is_active == True
    ).first()
    
    # Get recent progress
    recent_progress = db.query(ProgressRecord).filter(
        ProgressRecord.user_id == current_user.id
    ).order_by(ProgressRecord.recorded_at.desc()).limit(7).all()
    
    workouts_this_week = sum(1 for r in recent_progress if r.workout_completed)
    total_calories_burned = sum(r.calories_burned or 0 for r in recent_progress)
    
    # Calculate BMI
    bmi = None
    if current_user.height and current_user.weight:
        height_m = current_user.height / 100
        bmi = round(current_user.weight / (height_m ** 2), 1)
    
    return {
        "user_name": current_user.full_name,
        "fitness_goal": current_user.fitness_goal,
        "has_workout_plan": active_workout is not None,
        "has_nutrition_plan": active_nutrition is not None,
        "workouts_this_week": workouts_this_week,
        "total_calories_burned": round(total_calories_burned),
        "bmi": bmi,
        "current_weight": current_user.weight,
        "streak_days": workouts_this_week
    }
