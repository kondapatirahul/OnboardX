from pydantic import BaseModel, EmailStr
from typing import Optional
from app.models.models import UserRole


class RegisterRequest(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    role: UserRole = UserRole.EMPLOYEE
    organization_name: Optional[str] = None


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserOut"


class UserOut(BaseModel):
    id: str
    email: str
    full_name: str
    role: UserRole
    is_active: bool
    organization_id: Optional[str] = None

    class Config:
        from_attributes = True


LoginResponse.model_rebuild()
