import math
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.models import Employee, EmployeeStatus, User, UserRole
from app.repositories import employee_repository as repository
from app.schemas.employee import EmployeeCreate, EmployeeUpdate


def _require_organization(organization_id):
    if not organization_id:
        raise HTTPException(status_code=400, detail="User is not associated with an organization")


def _validate_relations(db: Session, organization_id, department_id=None, manager_id=None):
    if department_id and not repository.get_department(db, department_id, organization_id):
        raise HTTPException(status_code=400, detail="Department does not belong to this organization")
    if manager_id and not repository.get_manager(db, manager_id, organization_id):
        raise HTTPException(status_code=400, detail="Manager does not belong to this organization")


def _serialize(row):
    employee, user, department_name = row
    return {
        "id": str(employee.id),
        "employee_id": employee.employee_id,
        "user_id": str(user.id),
        "full_name": user.full_name,
        "email": user.email,
        "role": user.role,
        "is_active": user.is_active,
        "organization_id": str(employee.organization_id),
        "department_id": str(employee.department_id) if employee.department_id else None,
        "department_name": department_name,
        "designation": employee.designation,
        "joining_date": employee.joining_date,
        "manager_id": str(employee.manager_id) if employee.manager_id else None,
        "status": employee.status,
        "created_at": employee.created_at,
        "updated_at": employee.updated_at,
    }


def list_employees(
    db: Session, organization_id, search=None, department_id=None,
    status=None, page=1, page_size=20,
):
    _require_organization(organization_id)
    total = repository.count_employees(db, organization_id, search, department_id, status)
    rows = repository.search_employees(
        db, organization_id, search, department_id, status,
        offset=(page - 1) * page_size, limit=page_size,
    )
    return {
        "items": [_serialize(row) for row in rows],
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": math.ceil(total / page_size) if total else 0,
    }


def get_employee(db: Session, organization_id, employee_uuid: UUID):
    _require_organization(organization_id)
    row = repository.get_employee(db, employee_uuid, organization_id)
    if not row:
        raise HTTPException(status_code=404, detail="Employee not found")
    return _serialize(row)


def create_employee(db: Session, organization_id, data: EmployeeCreate):
    _require_organization(organization_id)
    if repository.get_by_employee_id(db, data.employee_id):
        raise HTTPException(status_code=409, detail="Employee ID already exists")
    if repository.get_by_email(db, str(data.email)):
        raise HTTPException(status_code=409, detail="Email already registered")

    department_id = data.department_id
    manager_id = data.manager_id
    _validate_relations(db, organization_id, department_id, manager_id)

    user = User(
        email=str(data.email).lower(),
        full_name=data.full_name,
        hashed_password=hash_password(data.temporary_password),
        role=UserRole.EMPLOYEE,
        is_active=True,
        organization_id=organization_id,
    )
    try:
        db.add(user)
        db.flush()
        employee = Employee(
            employee_id=data.employee_id,
            user_id=user.id,
            organization_id=organization_id,
            department_id=department_id,
            designation=data.designation,
            joining_date=data.joining_date,
            manager_id=manager_id,
            status=data.status,
        )
        db.add(employee)
        db.commit()
        db.refresh(employee)
        return get_employee(db, organization_id, employee.id)
    except Exception:
        db.rollback()
        raise


def update_employee(db: Session, organization_id, employee_uuid: UUID, data: EmployeeUpdate):
    _require_organization(organization_id)
    row = repository.get_employee(db, employee_uuid, organization_id)
    if not row:
        raise HTTPException(status_code=404, detail="Employee not found")
    employee, user, _ = row
    changes = data.model_dump(exclude_unset=True)

    if "email" in changes and changes["email"] is not None:
        email = str(changes["email"]).lower()
        existing = repository.get_by_email(db, email)
        if existing and existing.id != user.id:
            raise HTTPException(status_code=409, detail="Email already registered")
        user.email = email
    if "full_name" in changes and changes["full_name"] is not None:
        user.full_name = changes["full_name"]

    department_id = changes.get("department_id")
    manager_id = changes.get("manager_id")
    if "manager_id" in changes and manager_id == employee.id:
        raise HTTPException(status_code=400, detail="An employee cannot be their own manager")
    if "department_id" in changes or "manager_id" in changes:
        _validate_relations(
            db,
            organization_id,
            department_id if "department_id" in changes else employee.department_id,
            manager_id if "manager_id" in changes else employee.manager_id,
        )

    for field in ("department_id", "manager_id"):
        if field in changes:
            setattr(employee, field, changes[field])
    for field in ("designation", "joining_date", "status"):
        if field in changes:
            setattr(employee, field, changes[field])

    try:
        db.commit()
        db.refresh(employee)
    except Exception:
        db.rollback()
        raise
    return get_employee(db, organization_id, employee.id)


def deactivate_employee(db: Session, organization_id, employee_uuid: UUID):
    _require_organization(organization_id)
    row = repository.get_employee(db, employee_uuid, organization_id)
    if not row:
        raise HTTPException(status_code=404, detail="Employee not found")
    employee, user, _ = row
    employee.status = EmployeeStatus.INACTIVE
    user.is_active = False
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    return {"message": "Employee deactivated successfully", "employee_id": str(employee.id)}
