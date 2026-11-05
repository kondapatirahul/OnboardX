from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.models import (
    Department,
    Document,
    DocumentStatus,
    Employee,
    OnboardingInstance,
    OnboardingStatus,
)


def get_dashboard_stats(db: Session, organization_id) -> dict:
    """Return organization-scoped onboarding metrics for the HR dashboard."""
    employee_scope = Employee.organization_id == organization_id
    onboarding_scope = OnboardingInstance.organization_id == organization_id
    document_scope = Document.organization_id == organization_id

    total_employees = (
        db.query(func.count(Employee.id)).filter(employee_scope).scalar() or 0
    )
    active_onboarding = (
        db.query(func.count(OnboardingInstance.id))
        .filter(
            onboarding_scope,
            OnboardingInstance.status == OnboardingStatus.IN_PROGRESS,
        )
        .scalar()
        or 0
    )
    total_onboarding = (
        db.query(func.count(OnboardingInstance.id))
        .filter(onboarding_scope)
        .scalar()
        or 0
    )
    completed_onboarding = (
        db.query(func.count(OnboardingInstance.id))
        .filter(
            onboarding_scope,
            OnboardingInstance.status == OnboardingStatus.COMPLETED,
        )
        .scalar()
        or 0
    )
    pending_approvals = (
        db.query(func.count(Document.id))
        .filter(document_scope, Document.status == DocumentStatus.PENDING)
        .scalar()
        or 0
    )

    completion_percentage = (
        round(completed_onboarding / total_onboarding * 100, 1)
        if total_onboarding
        else 0.0
    )

    return {
        "total_employees": total_employees,
        "active_onboarding": active_onboarding,
        "pending_approvals": pending_approvals,
        "completed_onboarding": completed_onboarding,
        "completion_percentage": completion_percentage,
    }


def get_department_summary(db: Session, organization_id) -> list[dict]:
    rows = (
        db.query(Department.id, Department.name, func.count(Employee.id))
        .outerjoin(
            Employee,
            (Employee.department_id == Department.id)
            & (Employee.organization_id == organization_id),
        )
        .filter(Department.organization_id == organization_id)
        .group_by(Department.id, Department.name)
        .order_by(Department.name.asc())
        .all()
    )
    return [
        {
            "department_id": str(department_id),
            "department_name": name,
            "employee_count": count,
        }
        for department_id, name, count in rows
    ]
