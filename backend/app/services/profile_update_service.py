from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.repositories.profile_repository import get_profile_record
from app.schemas.profile import ProfileUpdate
from app.services.profile_read_service import get_my_profile


def update_my_profile(db: Session, current_user, data: ProfileUpdate):
    if current_user.organization_id is None:
        raise HTTPException(status_code=400, detail="User is not associated with an organization")
    row = get_profile_record(db, current_user.id, current_user.organization_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Employee profile not found")

    changes = data.model_dump(exclude_unset=True)
    if "full_name" in changes and changes["full_name"] is not None:
        current_user.full_name = changes["full_name"]

    try:
        db.commit()
        db.refresh(current_user)
    except Exception:
        db.rollback()
        raise
    return get_my_profile(db, current_user)
