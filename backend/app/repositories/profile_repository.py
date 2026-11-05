from sqlalchemy.orm import Session, aliased

from app.models.models import Department, Employee, User


def get_profile_record(db: Session, user_id, organization_id):
    manager_employee = aliased(Employee)
    manager_user = aliased(User)
    return (
        db.query(
            Employee,
            User,
            Department.name.label("department_name"),
            manager_user.full_name.label("manager_name"),
        )
        .join(User, User.id == Employee.user_id)
        .outerjoin(Department, Department.id == Employee.department_id)
        .outerjoin(manager_employee, manager_employee.id == Employee.manager_id)
        .outerjoin(manager_user, manager_user.id == manager_employee.user_id)
        .filter(Employee.user_id == user_id, Employee.organization_id == organization_id)
        .first()
    )
