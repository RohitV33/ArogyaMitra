from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import json

from app.database import get_db
from app.models.user import User, ProgressRecord
from app.routers.auth import get_current_user
from app.services.ai_agent import ai_agent

router = APIRouter()

class ProgressEntry(BaseModel):
    weight: Optional[float] = None
    body_fat_percentage: Optional[float] = None
    workout_completed: Optional[bool] = False
    calories_burned: Optional[float] = None
    calories_consumed: Optional[float] = None
    notes: Optional[str] = None

@router.post("/log")
async def log_progress(
    entry: ProgressEntry,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    record = ProgressRecord(
        user_id=current_user.id,
        weight=entry.weight,
        body_fat_percentage=entry.body_fat_percentage,
        workout_completed=entry.workout_completed,
        calories_burned=entry.calories_burned,
        calories_consumed=entry.calories_consumed,
        notes=entry.notes
    )
    db.add(record)
    db.commit()
    return {"message": "Progress logged successfully!", "record_id": record.id}

@router.get("/history")
async def get_progress_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    records = db.query(ProgressRecord).filter(
        ProgressRecord.user_id == current_user.id
    ).order_by(ProgressRecord.recorded_at.desc()).limit(30).all()
    
    return [{
        "id": r.id,
        "weight": r.weight,
        "body_fat_percentage": r.body_fat_percentage,
        "workout_completed": r.workout_completed,
        "calories_burned": r.calories_burned,
        "calories_consumed": r.calories_consumed,
        "notes": r.notes,
        "recorded_at": r.recorded_at
    } for r in records]

@router.get("/analytics")
async def get_progress_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    records = db.query(ProgressRecord).filter(
        ProgressRecord.user_id == current_user.id
    ).order_by(ProgressRecord.recorded_at.asc()).all()
    
    progress_data = [{
        "weight": r.weight,
        "calories_burned": r.calories_burned,
        "workout_completed": r.workout_completed,
        "recorded_at": str(r.recorded_at)
    } for r in records]
    
    analysis = ai_agent.analyze_progress(progress_data, current_user)
    
    # Basic stats
    weights = [r.weight for r in records if r.weight]
    workouts_done = sum(1 for r in records if r.workout_completed)
    
    return {
        "total_records": len(records),
        "workouts_completed": workouts_done,
        "weight_history": weights,
        "ai_analysis": analysis
    }
