import re
import uuid
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.models import User, Organization, UserRole
from app.core.security import hash_password, verify_password, create_access_token
from app.schemas.auth import RegisterRequest


def _slugify(name: str) -> str:
    slug = re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')
    return f"{slug}-{str(uuid.uuid4())[:8]}"


def register_user(db: Session, data: RegisterRequest) -> User:
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    org = None
    if data.role == UserRole.SUPER_ADMIN and data.organization_name:
        org = Organization(name=data.organization_name, slug=_slugify(data.organization_name))
        db.add(org)
        db.flush()

    user = User(
        email=data.email,
        full_name=data.full_name,
        hashed_password=hash_password(data.password),
        role=data.role,
        organization_id=org.id if org else None,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> User:
    user = db.query(User).filter(User.email == email, User.is_active == True).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    return user


def build_token_response(user: User) -> dict:
    token = create_access_token({"sub": str(user.id), "role": user.role.value})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role.value,
            "is_active": user.is_active,
            "organization_id": str(user.organization_id) if user.organization_id else None,
        },
    }
