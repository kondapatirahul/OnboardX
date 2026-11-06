from datetime import datetime
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.models import OnboardingStatus, TaskStatus
from app.repositories import onboarding_repository as repository
from app.services.onboarding_assignment_service import _instance_data


def _require_org(organization_id):
    if not organization_id:
        raise HTTPException(status_code=400, detail="User is not associated with an organization")


def update_instance_status(db: Session, organization_id, instance_id, status):
    _require_org(organization_id)
    instance = repository.get_instance(db, organization_id, instance_id)
    if not instance:
        raise HTTPException(status_code=404, detail="Onboarding instance not found")
    if status == OnboardingStatus.COMPLETED:
        if any(task.status != TaskStatus.COMPLETED for task in instance.tasks):
            raise HTTPException(status_code=409, detail="Complete all onboarding tasks before completing onboarding")
        instance.completed_at = datetime.utcnow()
    elif instance.status == OnboardingStatus.COMPLETED:
        instance.completed_at = None
    updated = repository.update_instance_status(db, instance, status)
    return _instance_data(updated)


def update_task_status(db: Session, organization_id, instance_id, task_id, status):
    _require_org(organization_id)
    task = repository.get_task(db, organization_id, instance_id, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Onboarding task not found")
    if task.status == TaskStatus.CANCELLED:
        raise HTTPException(status_code=409, detail="Cancelled tasks cannot be updated")
    task.status = status
    task.completed_at = datetime.utcnow() if status == TaskStatus.COMPLETED else None
    db.commit()
    instance = repository.get_instance(db, organization_id, instance_id)
    data = _instance_data(instance)
    total = len(instance.tasks)
    completed = sum(item.status == TaskStatus.COMPLETED for item in instance.tasks)
    instance.progress_percentage = round(completed / total * 100, 2) if total else 0.0
    if total and completed == total:
        instance.status = OnboardingStatus.COMPLETED
        instance.completed_at = datetime.utcnow()
    elif instance.status == OnboardingStatus.COMPLETED:
        instance.status = OnboardingStatus.IN_PROGRESS
        instance.completed_at = None
    db.commit()
    data.update({"status": instance.status, "progress_percentage": instance.progress_percentage,
                 "completed_at": instance.completed_at})
    return data
