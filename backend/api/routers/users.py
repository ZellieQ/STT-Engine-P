from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from api.db.database import get_db
from api.models.user import User
from api.schemas.user import UserResponse, UserUpdate
from api.routers.auth import get_current_active_user, get_password_hash

router = APIRouter()

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

@router.put("/me", response_model=UserResponse)
async def update_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Update user fields if provided
    if user_update.email is not None:
        # Check if email already exists
        email_exists = db.query(User).filter(
            User.email == user_update.email,
            User.id != current_user.id
        ).first()
        if email_exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        current_user.email = user_update.email
    
    if user_update.full_name is not None:
        current_user.full_name = user_update.full_name
    
    if user_update.password is not None:
        current_user.hashed_password = get_password_hash(user_update.password)
    
    db.commit()
    db.refresh(current_user)
    
    return current_user

@router.get("/usage")
async def get_usage_statistics(current_user: User = Depends(get_current_active_user)):
    return {
        "total_transcription_seconds": current_user.total_transcription_seconds,
        "total_transcription_count": current_user.total_transcription_count,
        "subscription_tier": current_user.subscription_tier,
        "subscription_expires": current_user.subscription_expires
    }
