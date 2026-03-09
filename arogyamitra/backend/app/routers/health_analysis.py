"""
Extended health analysis endpoint referenced in Activity 4.2 screenshot:
POST /api/health-analysis/analyze
"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional

from app.models.user import User
from app.routers.auth import get_current_user
from app.services.ai_agent import ai_agent

router = APIRouter()

class HealthAnalysisRequest(BaseModel):
    age: Optional[int] = None
    gender: Optional[str] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    bmi: Optional[float] = None
    medical_history: Optional[str] = "None"
    injuries: Optional[str] = "None"
    fitness_goal: Optional[str] = "general fitness"
    allergies: Optional[str] = "None"
    medications: Optional[str] = "None"
    lifestyle_notes: Optional[str] = None

@router.post("/analyze")
async def analyze_health(
    request: HealthAnalysisRequest,
    current_user: User = Depends(get_current_user)
):
    """AI-powered comprehensive health analysis endpoint"""
    prompt = f"""
    Perform a comprehensive health analysis for this user:
    
    Demographics: {request.age}yr {request.gender}, Height: {request.height}cm, Weight: {request.weight}kg, BMI: {request.bmi}
    Medical History: {request.medical_history}
    Injuries: {request.injuries}
    Allergies: {request.allergies}
    Medications: {request.medications}
    Fitness Goal: {request.fitness_goal}
    
    Provide:
    1. Risk assessment for their fitness journey
    2. Exercise modifications based on injuries/conditions
    3. Dietary guidance based on allergies/medications
    4. Specific warnings or precautions
    5. Top 3 personalized health recommendations
    
    Be specific, practical and safety-conscious.
    """
    
    analysis = ai_agent._call_groq(
        prompt,
        system_prompt="You are ArogyaMitra's health analysis AI. Provide safe, accurate, personalized health insights. Always recommend consulting a doctor for medical conditions.",
        max_tokens=800
    )
    
    return {
        "analysis": analysis,
        "bmi_risk": _get_bmi_risk(request.bmi),
        "exercise_clearance": _check_exercise_clearance(request.medical_history, request.injuries),
        "user": current_user.full_name
    }

def _get_bmi_risk(bmi: Optional[float]) -> str:
    if not bmi:
        return "unknown"
    if bmi < 18.5:
        return "underweight"
    if bmi < 25:
        return "healthy"
    if bmi < 30:
        return "overweight"
    return "obese"

def _check_exercise_clearance(medical_history: str, injuries: str) -> str:
    high_risk_conditions = ["heart", "cardiac", "diabetes", "hypertension", "surgery"]
    history_lower = (medical_history or "").lower()
    injuries_lower = (injuries or "").lower()
    
    for condition in high_risk_conditions:
        if condition in history_lower:
            return "consult_doctor_first"
    
    if "surgery" in injuries_lower or "fracture" in injuries_lower:
        return "modified_exercises_only"
    
    return "cleared_for_exercise"
