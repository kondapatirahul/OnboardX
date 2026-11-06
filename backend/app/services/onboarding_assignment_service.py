from datetime import datetime
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.models import OnboardingStatus
from app.repositories import onboarding_repository as repository


def _require_org(organization_id):
    if not organization_id:
        raise HTTPException(status_code=400, detail="User is not associated with an organization")


def _instance_data(instance):
    tasks = list(instance.tasks)
    total = len(tasks)
    completed = sum(task.status.value == "completed" for task in tasks)
    progress = round((completed / total) * 100, 2) if total else 0.0
    return {"id": instance.id, "employee_id": instance.employee_id,
            "template_id": instance.template_id, "status": instance.status,
            "progress_percentage": progress, "started_at": instance.started_at,
            "completed_at": instance.completed_at, "tasks": tasks}


def assign_template(db: Session, organization_id, employee_id, template_id):
    _require_org(organization_id)
    employee = repository.get_employee(db, organization_id, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found in this organization")
    template = repository.get_template(db, organization_id, template_id)
    if not template or not template.is_active:
        raise HTTPException(status_code=404, detail="Active onboarding template not found")
    existing = next((item for item in repository.list_instances(db, organization_id, employee_id)
                     if item.status != OnboardingStatus.COMPLETED), None)
    if existing:
        raise HTTPException(status_code=409, detail="Employee already has an active onboarding")
    instance = repository.create_instance(db, organization_id, employee, template)
    instance.started_at = datetime.utcnow()
    db.commit()
    return _instance_data(instance)


def list_instances(db: Session, organization_id, employee_id=None):
    _require_org(organization_id)
    return [_instance_data(item) for item in repository.list_instances(db, organization_id, employee_id)]
