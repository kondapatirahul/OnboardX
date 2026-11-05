from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.security import decode_token
from app.models.models import User, UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    user = db.query(User).filter(User.id == payload.get("sub"), User.is_active == True).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


def require_roles(*roles: UserRole):
    def checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return current_user
    return checker


def require_hr_or_above(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role not in (UserRole.HR_ADMIN, UserRole.SUPER_ADMIN):
        raise HTTPException(status_code=403, detail="HR Admin or above required")
    return current_user


def require_manager_or_above(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role not in (UserRole.MANAGER, UserRole.HR_ADMIN, UserRole.SUPER_ADMIN):
        raise HTTPException(status_code=403, detail="Manager or above required")
    return current_user
