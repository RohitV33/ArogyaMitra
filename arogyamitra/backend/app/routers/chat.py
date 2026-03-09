from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Dict

from app.database import get_db
from app.models.user import User, ChatSession
from app.routers.auth import get_current_user
from app.services.ai_agent import ai_agent
import json

router = APIRouter()

class ChatMessage(BaseModel):
    message: str
    user_status: Optional[str] = "normal"
    workout_plan: Optional[Dict] = None
    nutrition_plan: Optional[Dict] = None

@router.post("/aromi")
async def chat_with_aromi(
    chat: ChatMessage,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Chat with AROMI AI Coach"""
    context = {
        "user_status": chat.user_status,
        "workout_plan": chat.workout_plan,
        "nutrition_plan": chat.nutrition_plan
    }
    
    response = ai_agent.chat_with_aromi(chat.message, current_user, context)
    
    # Save chat session
    session = ChatSession(
        user_id=current_user.id,
        messages=json.dumps([
            {"role": "user", "content": chat.message},
            {"role": "aromi", "content": response}
        ]),
        session_type="general"
    )
    db.add(session)
    db.commit()
    
    return {"response": response, "coach": "AROMI"}

@router.get("/history")
async def get_chat_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    sessions = db.query(ChatSession).filter(
        ChatSession.user_id == current_user.id
    ).order_by(ChatSession.created_at.desc()).limit(20).all()
    
    return [{
        "id": s.id,
        "messages": json.loads(s.messages),
        "created_at": s.created_at
    } for s in sessions]
