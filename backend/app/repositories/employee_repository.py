from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.models import Department, Employee, User


def get_employee_query(db: Session, organization_id):
    return (
        db.query(Employee, User, Department.name.label("department_name"))
        .join(User, User.id == Employee.user_id)
        .outerjoin(Department, Department.id == Employee.department_id)
        .filter(Employee.organization_id == organization_id)
    )


def get_by_employee_id(db: Session, employee_id: str):
    return db.query(Employee).filter(Employee.employee_id == employee_id).first()


def get_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def get_department(db: Session, department_id: str, organization_id):
    return (
        db.query(Department)
        .filter(
            Department.id == department_id,
            Department.organization_id == organization_id,
        )
        .first()
    )


def get_manager(db: Session, manager_id: str, organization_id):
    return (
        db.query(Employee)
        .filter(
            Employee.id == manager_id,
            Employee.organization_id == organization_id,
        )
        .first()
    )


def search_employees(
    db: Session,
    organization_id,
    search: str | None = None,
    department_id: str | None = None,
    status=None,
    offset: int = 0,
    limit: int = 20,
):
    query = get_employee_query(db, organization_id)
    if search:
        pattern = f"%{search.strip()}%"
        query = query.filter(
            or_(
                Employee.employee_id.ilike(pattern),
                User.full_name.ilike(pattern),
                User.email.ilike(pattern),
                Employee.designation.ilike(pattern),
            )
        )
    if department_id:
        query = query.filter(Employee.department_id == department_id)
    if status:
        query = query.filter(Employee.status == status)
    return query.order_by(Employee.created_at.desc()).offset(offset).limit(limit).all()


def count_employees(
    db: Session,
    organization_id,
    search: str | None = None,
    department_id: str | None = None,
    status=None,
) -> int:
    query = db.query(Employee).join(User, User.id == Employee.user_id).filter(
        Employee.organization_id == organization_id
    )
    if search:
        pattern = f"%{search.strip()}%"
        query = query.filter(
            or_(
                Employee.employee_id.ilike(pattern),
                User.full_name.ilike(pattern),
                User.email.ilike(pattern),
                Employee.designation.ilike(pattern),
            )
        )
    if department_id:
        query = query.filter(Employee.department_id == department_id)
    if status:
        query = query.filter(Employee.status == status)
    return query.count()


def get_employee(db: Session, employee_uuid, organization_id):
    return (
        get_employee_query(db, organization_id)
        .filter(Employee.id == employee_uuid)
        .first()
    )
