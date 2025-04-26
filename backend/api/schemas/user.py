from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None

class UserResponse(UserBase):
    id: int
    is_active: bool
    subscription_tier: str
    created_at: datetime
    
    class Config:
        orm_mode = True

class UserInDB(UserResponse):
    hashed_password: str
    is_superuser: bool
    subscription_expires: Optional[datetime] = None
    total_transcription_seconds: int
    total_transcription_count: int
    updated_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True
