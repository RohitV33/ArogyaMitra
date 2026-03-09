from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Dict

from app.database import get_db
from app.models.user import User
from app.routers.auth import get_current_user
from app.services.ai_agent import ai_agent

router = APIRouter()

class ArogyaCoachMessage(BaseModel):
    message: str
    user_status: Optional[str] = "normal"  # normal, traveling, recovering, busy
    workout_plan: Optional[Dict] = None
    nutrition_plan: Optional[Dict] = None

class DynamicPlanAdjustmentRequest(BaseModel):
    reason: str  # "travel", "health_issue", "time_constraint"
    duration_days: int
    current_plan: Dict
    user_data: Dict

@router.post("/aromi-chat")
async def aromi_coach_chat(
    request: ArogyaCoachMessage,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Chat with AROMI AI Coach for real-time adaptive wellness guidance"""
    context = {
        "user_status": request.user_status,
        "workout_plan": request.workout_plan,
        "nutrition_plan": request.nutrition_plan
    }
    
    response = ai_agent.chat_with_aromi(request.message, current_user, context)
    
    return {
        "response": response,
        "coach": "AROMI",
        "user": current_user.full_name
    }

@router.post("/adjust-plan")
async def adjust_plan_dynamically(
    request: DynamicPlanAdjustmentRequest,
    current_user: User = Depends(get_current_user)
):
    """Dynamically adjust workout/nutrition plan based on life changes"""
    from app.services.ai_agent import ai_agent
    
    prompt = f"""
    User needs plan adjustment:
    Reason: {request.reason}
    Duration: {request.duration_days} days
    
    Current Plan: {request.current_plan}
    
    Provide a modified plan that accommodates this change while maintaining progress toward fitness goals.
    Return JSON with adjusted_plan and explanation.
    """
    
    response = ai_agent._call_groq(prompt, max_tokens=1000)
    
    return {
        "adjusted_plan": response,
        "reason": request.reason,
        "duration_days": request.duration_days
    }

@router.get("/motivate")
async def get_daily_motivation(
    current_user: User = Depends(get_current_user)
):
    """Get personalized daily motivation"""
    prompt = f"""Give a short (2-3 sentences), powerful motivational message for {current_user.full_name} 
    who is working towards {current_user.fitness_goal.value if current_user.fitness_goal else 'fitness goals'}. 
    Make it personal, energetic, and actionable. Include an emoji."""
    
    motivation = ai_agent._call_groq(prompt, max_tokens=100)
    
    return {"motivation": motivation, "name": current_user.full_name}
