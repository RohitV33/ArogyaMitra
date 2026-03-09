from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import json

from app.database import get_db
from app.models.user import User, HealthAssessment
from app.routers.auth import get_current_user

router = APIRouter()

class HealthAssessmentInput(BaseModel):
    systolic_bp: Optional[float] = None
    diastolic_bp: Optional[float] = None
    resting_heart_rate: Optional[float] = None
    sleep_hours: Optional[float] = None
    stress_level: Optional[int] = None  # 1-10
    water_intake_liters: Optional[float] = None
    smoking: Optional[bool] = False
    alcohol_frequency: Optional[str] = None
    medical_conditions: Optional[str] = None

@router.post("/assess")
async def create_health_assessment(
    assessment_input: HealthAssessmentInput,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a comprehensive health assessment"""
    # Calculate BMI
    bmi = None
    if current_user.height and current_user.weight:
        height_m = current_user.height / 100
        bmi = round(current_user.weight / (height_m ** 2), 1)
    
    # Calculate health score (simple algorithm)
    health_score = 70  # Base score
    if bmi:
        if 18.5 <= bmi <= 24.9:
            health_score += 10
        elif bmi < 18.5 or bmi > 30:
            health_score -= 10
    
    if assessment_input.sleep_hours:
        if 7 <= assessment_input.sleep_hours <= 9:
            health_score += 10
        elif assessment_input.sleep_hours < 6:
            health_score -= 10
    
    if assessment_input.stress_level:
        if assessment_input.stress_level <= 3:
            health_score += 5
        elif assessment_input.stress_level >= 8:
            health_score -= 10
    
    if assessment_input.smoking:
        health_score -= 15
    
    health_score = max(0, min(100, health_score))
    
    # Generate recommendations
    recommendations = []
    if bmi and bmi > 25:
        recommendations.append("Consider a calorie-controlled diet to reach a healthy BMI")
    if assessment_input.sleep_hours and assessment_input.sleep_hours < 7:
        recommendations.append("Aim for 7-9 hours of sleep for optimal recovery")
    if assessment_input.stress_level and assessment_input.stress_level > 7:
        recommendations.append("Practice stress management techniques like meditation")
    if assessment_input.water_intake_liters and assessment_input.water_intake_liters < 2:
        recommendations.append("Increase water intake to at least 2-3 liters per day")
    
    if not recommendations:
        recommendations.append("Keep up the great work maintaining your health!")
    
    assessment = HealthAssessment(
        user_id=current_user.id,
        assessment_data=json.dumps(assessment_input.dict()),
        bmi=bmi,
        health_score=health_score,
        recommendations=json.dumps(recommendations)
    )
    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    
    bmi_category = "Normal" if bmi and 18.5 <= bmi <= 24.9 else ("Underweight" if bmi and bmi < 18.5 else ("Overweight" if bmi and bmi <= 29.9 else "Obese"))
    
    return {
        "assessment_id": assessment.id,
        "bmi": bmi,
        "bmi_category": bmi_category,
        "health_score": health_score,
        "health_grade": "A" if health_score >= 90 else ("B" if health_score >= 75 else ("C" if health_score >= 60 else "D")),
        "recommendations": recommendations
    }

@router.get("/latest")
async def get_latest_assessment(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    assessment = db.query(HealthAssessment).filter(
        HealthAssessment.user_id == current_user.id
    ).order_by(HealthAssessment.created_at.desc()).first()
    
    if not assessment:
        return {"message": "No assessment found. Take your first health assessment!"}
    
    return {
        "bmi": assessment.bmi,
        "health_score": assessment.health_score,
        "recommendations": json.loads(assessment.recommendations) if assessment.recommendations else [],
        "created_at": assessment.created_at
    }
