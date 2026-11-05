from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import require_hr_or_above
from app.db.session import get_db
from app.models.models import User
from app.schemas.dashboard import DashboardStats, DepartmentSummary
from app.services.dashboard_service import get_dashboard_stats, get_department_summary

router = APIRouter()


def _organization_id(user: User):
    if not user.organization_id:
        raise HTTPException(status_code=400, detail="User is not associated with an organization")
    return user.organization_id


@router.get("/stats", response_model=DashboardStats)
def dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_hr_or_above),
):
    return get_dashboard_stats(db, _organization_id(current_user))


@router.get("/departments", response_model=list[DepartmentSummary])
def department_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_hr_or_above),
):
    return get_department_summary(db, _organization_id(current_user))
