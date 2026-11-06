import re
import uuid

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password, create_access_token
from app.models.models import User, Organization, UserRole, Employee, EmployeeStatus
from app.schemas.auth import RegisterRequest


def _slugify(name: str) -> str:
    base = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-") or "organization"
    return f"{base[:88]}-{uuid.uuid4().hex[:8]}"


def resolve_organization(db: Session, organization_code: str) -> Organization:
    code = organization_code.strip().lower()
    organization = db.query(Organization).filter(Organization.slug == code).first()
    if not organization or not organization.is_active:
        raise HTTPException(status_code=404, detail="Organization code is invalid or inactive")
    return organization


def register_user(db: Session, data: RegisterRequest) -> tuple[User, str | None]:
    email = data.email.strip().lower()
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=409, detail="An account with this email already exists")

    organization = None
    organization_code = None

    if data.role == UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Super Admin accounts cannot be created through public signup")

    if data.role == UserRole.HR_ADMIN:
        if not data.organization_name:
            raise HTTPException(status_code=422, detail="Organization name is required for HR Admin signup")
        organization = Organization(name=data.organization_name, slug=_slugify(data.organization_name))
        db.add(organization)
        db.flush()
        organization_code = organization.slug
    else:
        if data.role == UserRole.MANAGER:
            raise HTTPException(status_code=403, detail="Manager accounts must be created by an HR Admin")
        if not data.organization_code:
            raise HTTPException(status_code=422, detail="Enter your organization's signup code")
        organization = resolve_organization(db, data.organization_code)

    user = User(
        email=email,
        full_name=data.full_name,
        hashed_password=hash_password(data.password),
        role=data.role,
        organization_id=organization.id,
    )
    db.add(user)
    db.flush()

    if data.role == UserRole.EMPLOYEE:
        employee = Employee(
            employee_id=f"ONX-{uuid.uuid4().hex[:10].upper()}",
            user_id=user.id,
            organization_id=organization.id,
            status=EmployeeStatus.ONBOARDING,
        )
        db.add(employee)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="An account with this email already exists") from exc
    except Exception:
        db.rollback()
        raise
    db.refresh(user)
    return user, organization_code


def authenticate_user(db: Session, email: str, password: str) -> User:
    user = db.query(User).filter(User.email == email.strip().lower(), User.is_active.is_(True)).first()
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
