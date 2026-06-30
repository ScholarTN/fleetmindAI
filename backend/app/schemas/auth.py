from pydantic import BaseModel, EmailStr
from app.models.user import UserRole
from datetime import datetime


class UserRegister(BaseModel):
    email: EmailStr
    full_name: str
    password: str
    role: UserRole = UserRole.DISPATCHER


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: str
    email: str
    full_name: str
    role: UserRole
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
