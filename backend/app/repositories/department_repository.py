from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.models import Department, Employee


def list_departments(db: Session, organization_id):
    return (
        db.query(Department, func.count(Employee.id).label("employee_count"))
        .outerjoin(Employee, Employee.department_id == Department.id)
        .filter(Department.organization_id == organization_id)
        .group_by(Department.id)
        .order_by(func.lower(Department.name).asc())
        .all()
    )


def get_department(db: Session, department_id, organization_id):
    return (
        db.query(Department)
        .filter(
            Department.id == department_id,
            Department.organization_id == organization_id,
        )
        .first()
    )


def get_department_by_name(db: Session, organization_id, name: str):
    return (
        db.query(Department)
        .filter(
            Department.organization_id == organization_id,
            func.lower(Department.name) == name.lower(),
        )
        .first()
    )


def count_department_employees(db: Session, department_id, organization_id) -> int:
    return (
        db.query(Employee)
        .filter(
            Employee.department_id == department_id,
            Employee.organization_id == organization_id,
        )
        .count()
    )


def create_department(db: Session, organization_id, name: str):
    department = Department(name=name, organization_id=organization_id)
    db.add(department)
    db.commit()
    db.refresh(department)
    return department
