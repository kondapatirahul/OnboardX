"""Create repeatable local demo accounts for an OnboardX presentation environment.

Run from the backend directory with: python -m app.seed_demo
This utility refuses to run outside APP_ENV=development.
"""

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.models import (
    Department,
    Employee,
    EmployeeStatus,
    Organization,
    User,
    UserRole,
)

DEMO_ORG_CODE = "onboardx-demo"
DEMO_ACCOUNTS = (
    {
        "email": "hr.demo@onboardx.local",
        "password": "OnboardX-HR-Demo-2026!",
        "name": "Olivia HR Demo",
        "role": UserRole.HR_ADMIN,
    },
    {
        "email": "employee.demo@onboardx.local",
        "password": "OnboardX-Employee-Demo-2026!",
        "name": "Alex Employee Demo",
        "role": UserRole.EMPLOYEE,
    },
)


def ensure_demo_data(db: Session) -> None:
    organization = db.query(Organization).filter(Organization.slug == DEMO_ORG_CODE).first()
    if organization is None:
        organization = Organization(name="OnboardX Demo Company", slug=DEMO_ORG_CODE)
        db.add(organization)
        db.flush()

    department = (
        db.query(Department)
        .filter(
            Department.organization_id == organization.id,
            Department.name == "People Operations",
        )
        .first()
    )
    if department is None:
        department = Department(name="People Operations", organization_id=organization.id)
        db.add(department)
        db.flush()

    for account in DEMO_ACCOUNTS:
        user = db.query(User).filter(User.email == account["email"]).first()
        if user is None:
            user = User(
                email=account["email"],
                full_name=account["name"],
                hashed_password=hash_password(account["password"]),
                role=account["role"],
                organization_id=organization.id,
                is_active=True,
            )
            db.add(user)
            db.flush()
        else:
            user.organization_id = organization.id
            user.role = account["role"]
            user.is_active = True

        if account["role"] == UserRole.EMPLOYEE:
            employee = db.query(Employee).filter(Employee.user_id == user.id).first()
            if employee is None:
                db.add(
                    Employee(
                        employee_id="ONX-DEMO-001",
                        user_id=user.id,
                        organization_id=organization.id,
                        department_id=department.id,
                        designation="People Operations Associate",
                        status=EmployeeStatus.ACTIVE,
                    )
                )

    db.commit()


def main() -> None:
    if settings.APP_ENV.lower() != "development":
        raise SystemExit("Demo accounts can only be seeded when APP_ENV=development")

    db = SessionLocal()
    try:
        ensure_demo_data(db)
    finally:
        db.close()

    print("OnboardX demo accounts are ready.")
    print(f"Organization code: {DEMO_ORG_CODE}")
    for account in DEMO_ACCOUNTS:
        print(f"{account['role'].value}: {account['email']} / {account['password']}")


if __name__ == "__main__":
    main()
