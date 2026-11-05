from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.models import User
from app.schemas.profile import ProfileResponse, ProfileUpdate
from app.services.profile_update_service import update_my_profile

router = APIRouter()


@router.patch("/me", response_model=ProfileResponse)
def profile_me_update(
    data: ProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return update_my_profile(db, current_user, data)
