from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.models import User
from app.schemas.profile import ProfileResponse
from app.services.profile_read_service import get_my_profile

router = APIRouter()


@router.get("/me", response_model=ProfileResponse)
def profile_me(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_my_profile(db, current_user)
