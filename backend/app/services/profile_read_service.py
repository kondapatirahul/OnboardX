from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.repositories.profile_repository import get_profile_record


def serialize_profile(row):
    employee, user, department_name, manager_name = row
    return {
        "employee_id": employee.employee_id,
        "user_id": user.id,
        "full_name": user.full_name,
        "email": user.email,
        "role": user.role,
        "designation": employee.designation,
        "department_id": employee.department_id,
        "department_name": department_name,
        "manager_id": employee.manager_id,
        "manager_name": manager_name,
        "joining_date": employee.joining_date,
        "status": employee.status,
        "account_active": user.is_active,
        "created_at": employee.created_at,
        "updated_at": employee.updated_at,
    }


def get_my_profile(db: Session, current_user):
    if current_user.organization_id is None:
        raise HTTPException(status_code=400, detail="User is not associated with an organization")
    row = get_profile_record(db, current_user.id, current_user.organization_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Employee profile not found")
    return serialize_profile(row)
