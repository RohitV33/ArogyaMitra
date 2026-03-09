from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import json

from app.database import get_db
from app.models.user import User, NutritionPlan
from app.routers.auth import get_current_user
from app.services.ai_agent import ai_agent

router = APIRouter()

@router.post("/generate")
async def generate_nutrition_plan(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    plan_data = ai_agent.generate_nutrition_plan(current_user)
    
    db.query(NutritionPlan).filter(
        NutritionPlan.user_id == current_user.id,
        NutritionPlan.is_active == True
    ).update({"is_active": False})
    
    new_plan = NutritionPlan(
        user_id=current_user.id,
        plan_data=json.dumps(plan_data),
        daily_calories=plan_data.get("daily_calories", 2000),
        protein_grams=plan_data.get("macros", {}).get("protein", 150),
        carb_grams=plan_data.get("macros", {}).get("carbs", 225),
        fat_grams=plan_data.get("macros", {}).get("fat", 67),
        is_active=True
    )
    db.add(new_plan)
    db.commit()
    db.refresh(new_plan)
    
    return {"plan_id": new_plan.id, "plan": plan_data, "message": "Nutrition plan generated!"}

@router.get("/current")
async def get_current_nutrition_plan(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    plan = db.query(NutritionPlan).filter(
        NutritionPlan.user_id == current_user.id,
        NutritionPlan.is_active == True
    ).order_by(NutritionPlan.created_at.desc()).first()
    
    if not plan:
        raise HTTPException(status_code=404, detail="No active nutrition plan found.")
    
    return {
        "plan_id": plan.id,
        "plan": json.loads(plan.plan_data),
        "daily_calories": plan.daily_calories,
        "macros": {"protein": plan.protein_grams, "carbs": plan.carb_grams, "fat": plan.fat_grams},
        "created_at": plan.created_at
    }
