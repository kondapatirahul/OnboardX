from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.deps import require_hr_or_above
from app.db.session import get_db
from app.models.models import User
from app.schemas.department import (
    DepartmentCreate,
    DepartmentListResponse,
    DepartmentResponse,
    DepartmentUpdate,
)
from app.services.department_service import (
    create_department,
    delete_department,
    list_departments,
    update_department,
)

router = APIRouter()


@router.get("", response_model=DepartmentListResponse)
def departments_list(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_hr_or_above),
):
    return list_departments(db, current_user.organization_id)


@router.post("", response_model=DepartmentResponse, status_code=status.HTTP_201_CREATED)
def departments_create(
    data: DepartmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_hr_or_above),
):
    return create_department(db, current_user.organization_id, data)


@router.patch("/{department_id}", response_model=DepartmentResponse)
def departments_update(
    department_id: UUID,
    data: DepartmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_hr_or_above),
):
    return update_department(db, current_user.organization_id, department_id, data)


@router.delete("/{department_id}")
def departments_delete(
    department_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_hr_or_above),
):
    return delete_department(db, current_user.organization_id, department_id)
