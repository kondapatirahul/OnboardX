from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.repositories import department_repository as repository
from app.schemas.department import DepartmentCreate, DepartmentUpdate


def _require_organization(organization_id):
    if not organization_id:
        raise HTTPException(status_code=400, detail="User is not associated with an organization")


def _serialize(row):
    department, employee_count = row
    return {
        "id": department.id,
        "name": department.name,
        "organization_id": department.organization_id,
        "employee_count": employee_count,
        "created_at": department.created_at,
    }


def list_departments(db: Session, organization_id):
    _require_organization(organization_id)
    rows = repository.list_departments(db, organization_id)
    return {"items": [_serialize(row) for row in rows], "total": len(rows)}


def create_department(db: Session, organization_id, data: DepartmentCreate):
    _require_organization(organization_id)
    if repository.get_department_by_name(db, organization_id, data.name):
        raise HTTPException(status_code=409, detail="A department with this name already exists")
    try:
        department = repository.create_department(db, organization_id, data.name)
        return _serialize((department, 0))
    except Exception:
        db.rollback()
        raise


def update_department(db: Session, organization_id, department_id, data: DepartmentUpdate):
    _require_organization(organization_id)
    department = repository.get_department(db, department_id, organization_id)
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    duplicate = repository.get_department_by_name(db, organization_id, data.name)
    if duplicate and duplicate.id != department.id:
        raise HTTPException(status_code=409, detail="A department with this name already exists")
    department.name = data.name
    try:
        db.commit()
        db.refresh(department)
    except Exception:
        db.rollback()
        raise
    employee_count = repository.count_department_employees(db, department.id, organization_id)
    return _serialize((department, employee_count))


def delete_department(db: Session, organization_id, department_id):
    _require_organization(organization_id)
    department = repository.get_department(db, department_id, organization_id)
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    employee_count = repository.count_department_employees(db, department.id, organization_id)
    if employee_count:
        raise HTTPException(
            status_code=409,
            detail="Department cannot be deleted while employees are assigned to it",
        )
    try:
        db.delete(department)
        db.commit()
    except Exception:
        db.rollback()
        raise
    return {"message": "Department deleted successfully", "department_id": str(department_id)}
