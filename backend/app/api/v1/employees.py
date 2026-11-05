from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import require_hr_or_above
from app.db.session import get_db
from app.models.models import EmployeeStatus, User
from app.schemas.employee import (
    EmployeeCreate,
    EmployeeListResponse,
    EmployeeResponse,
    EmployeeUpdate,
)
from app.services.employee_service import (
    create_employee,
    deactivate_employee,
    get_employee,
    list_employees,
    update_employee,
)

router = APIRouter()


def _organization_id(user: User):
    return user.organization_id


@router.get("", response_model=EmployeeListResponse)
def employees_list(
    search: str | None = Query(default=None, max_length=100),
    department_id: UUID | None = None,
    status: EmployeeStatus | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_hr_or_above),
):
    return list_employees(
        db,
        _organization_id(current_user),
        search=search,
        department_id=department_id,
        status=status,
        page=page,
        page_size=page_size,
    )


@router.post("", response_model=EmployeeResponse, status_code=201)
def employees_create(
    data: EmployeeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_hr_or_above),
):
    return create_employee(db, _organization_id(current_user), data)


@router.get("/{employee_uuid}", response_model=EmployeeResponse)
def employees_get(
    employee_uuid: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_hr_or_above),
):
    return get_employee(db, _organization_id(current_user), employee_uuid)


@router.patch("/{employee_uuid}", response_model=EmployeeResponse)
def employees_update(
    employee_uuid: UUID,
    data: EmployeeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_hr_or_above),
):
    return update_employee(db, _organization_id(current_user), employee_uuid, data)


@router.delete("/{employee_uuid}")
def employees_deactivate(
    employee_uuid: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_hr_or_above),
):
    return deactivate_employee(db, _organization_id(current_user), employee_uuid)
