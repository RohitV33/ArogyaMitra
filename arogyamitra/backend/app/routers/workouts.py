from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import json

from app.database import get_db
from app.models.user import User, WorkoutPlan
from app.routers.auth import get_current_user
from app.services.ai_agent import ai_agent

router = APIRouter()

@router.post("/generate")
async def generate_workout_plan(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate AI-powered personalized workout plan"""
    plan_data = ai_agent.generate_workout_plan(current_user)
    
    # Deactivate old plans
    db.query(WorkoutPlan).filter(
        WorkoutPlan.user_id == current_user.id,
        WorkoutPlan.is_active == True
    ).update({"is_active": False})
    
    # Save new plan
    new_plan = WorkoutPlan(
        user_id=current_user.id,
        plan_data=json.dumps(plan_data),
        is_active=True
    )
    db.add(new_plan)
    db.commit()
    db.refresh(new_plan)
    
    return {"plan_id": new_plan.id, "plan": plan_data, "message": "Workout plan generated successfully!"}

@router.get("/current")
async def get_current_workout_plan(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's active workout plan"""
    plan = db.query(WorkoutPlan).filter(
        WorkoutPlan.user_id == current_user.id,
        WorkoutPlan.is_active == True
    ).order_by(WorkoutPlan.created_at.desc()).first()
    
    if not plan:
        raise HTTPException(status_code=404, detail="No active workout plan found. Generate one first!")
    
    return {"plan_id": plan.id, "plan": json.loads(plan.plan_data), "created_at": plan.created_at}

@router.get("/history")
async def get_workout_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get workout plan history"""
    plans = db.query(WorkoutPlan).filter(
        WorkoutPlan.user_id == current_user.id
    ).order_by(WorkoutPlan.created_at.desc()).limit(5).all()
    
    return [{"plan_id": p.id, "created_at": p.created_at, "is_active": p.is_active} for p in plans]
