from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt
import bcrypt
import traceback

from app.database import get_db
from app.models.user import User, FitnessGoal, WorkoutPreference, DietPreference
from app.utils.config import settings

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


class UserRegister(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: str
    age: Optional[int] = None
    gender: Optional[str] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    fitness_level: Optional[str] = "beginner"
    fitness_goal: Optional[str] = "maintenance"
    workout_preference: Optional[str] = "home"
    diet_preference: Optional[str] = "vegetarian"


class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    username: str
    full_name: str


# ─── Password helpers using bcrypt directly (no passlib) ──────────────────────
def get_password_hash(password: str) -> str:
    # Truncate to 72 bytes — bcrypt hard limit
    secret = password.encode("utf-8")[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(secret, salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    secret = plain_password.encode("utf-8")[:72]
    return bcrypt.checkpw(secret, hashed_password.encode("utf-8"))


# ─── JWT helpers ──────────────────────────────────────────────────────────────
def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    to_encode["sub"] = str(to_encode["sub"])   # sub must be string
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        sub = payload.get("sub")
        if sub is None:
            raise credentials_exception
        user_id = int(sub)
    except (JWTError, ValueError, TypeError):
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user


# ─── Enum helpers ─────────────────────────────────────────────────────────────
def _safe_fitness_goal(v):
    try:
        return FitnessGoal(v) if v else FitnessGoal.MAINTENANCE
    except ValueError:
        return FitnessGoal.MAINTENANCE

def _safe_workout_pref(v):
    try:
        return WorkoutPreference(v) if v else WorkoutPreference.HOME
    except ValueError:
        return WorkoutPreference.HOME

def _safe_diet_pref(v):
    try:
        return DietPreference(v) if v else DietPreference.VEGETARIAN
    except ValueError:
        return DietPreference.VEGETARIAN


# ─── Routes ───────────────────────────────────────────────────────────────────
@router.post("/register", response_model=Token)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    try:
        if db.query(User).filter(User.email == user_data.email).first():
            raise HTTPException(status_code=400, detail="Email already registered")
        if db.query(User).filter(User.username == user_data.username).first():
            raise HTTPException(status_code=400, detail="Username already taken")

        db_user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=get_password_hash(user_data.password),
            full_name=user_data.full_name,
            age=user_data.age,
            gender=user_data.gender,
            height=user_data.height,
            weight=user_data.weight,
            fitness_level=user_data.fitness_level or "beginner",
            fitness_goal=_safe_fitness_goal(user_data.fitness_goal),
            workout_preference=_safe_workout_pref(user_data.workout_preference),
            diet_preference=_safe_diet_pref(user_data.diet_preference),
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        access_token = create_access_token(data={"sub": db_user.id})
        return Token(
            access_token=access_token,
            token_type="bearer",
            user_id=db_user.id,
            username=db_user.username,
            full_name=db_user.full_name,
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"[REGISTER ERROR]\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    try:
        user = db.query(User).filter(
            (User.username == form_data.username) | (User.email == form_data.username)
        ).first()

        if not user or not verify_password(form_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
            )

        access_token = create_access_token(data={"sub": user.id})
        return Token(
            access_token=access_token,
            token_type="bearer",
            user_id=user.id,
            username=user.username,
            full_name=user.full_name,
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"[LOGIN ERROR]\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")


@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
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
        "role": current_user.role,
        "created_at": current_user.created_at,
    }