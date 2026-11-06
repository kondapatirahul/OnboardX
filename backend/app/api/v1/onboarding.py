from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.core.deps import require_hr_or_above
from app.db.session import get_db
from app.models.models import User
from app.schemas.onboarding import (
    OnboardingAssignmentCreate, OnboardingInstanceResponse,
    OnboardingStatusUpdate, OnboardingTaskStatusUpdate, OnboardingTemplateCreate,
    OnboardingTemplateListResponse, OnboardingTemplateResponse,
    OnboardingTemplateUpdate,
)
from app.services import onboarding_assignment_service, onboarding_progress_service, onboarding_template_service

router = APIRouter()


@router.get("/templates", response_model=OnboardingTemplateListResponse)
def templates_list(db: Session = Depends(get_db), current_user: User = Depends(require_hr_or_above)):
    return onboarding_template_service.list_templates(db, current_user.organization_id)


@router.post("/templates", response_model=OnboardingTemplateResponse, status_code=status.HTTP_201_CREATED)
def templates_create(data: OnboardingTemplateCreate, db: Session = Depends(get_db),
                    current_user: User = Depends(require_hr_or_above)):
    return onboarding_template_service.create_template(db, current_user.organization_id, current_user.id, data)


@router.patch("/templates/{template_id}", response_model=OnboardingTemplateResponse)
def templates_update(template_id: UUID, data: OnboardingTemplateUpdate,
                     db: Session = Depends(get_db), current_user: User = Depends(require_hr_or_above)):
    return onboarding_template_service.update_template(db, current_user.organization_id, template_id, data)


@router.post("/assignments", response_model=OnboardingInstanceResponse, status_code=status.HTTP_201_CREATED)
def assignments_create(data: OnboardingAssignmentCreate, db: Session = Depends(get_db),
                       current_user: User = Depends(require_hr_or_above)):
    return onboarding_assignment_service.assign_template(db, current_user.organization_id, data.employee_id, data.template_id)


@router.get("/instances", response_model=list[OnboardingInstanceResponse])
def instances_list(employee_id: UUID | None = Query(default=None), db: Session = Depends(get_db),
                   current_user: User = Depends(require_hr_or_above)):
    return onboarding_assignment_service.list_instances(db, current_user.organization_id, employee_id)


@router.patch("/instances/{instance_id}/status", response_model=OnboardingInstanceResponse)
def instances_update_status(instance_id: UUID, data: OnboardingStatusUpdate,
                            db: Session = Depends(get_db), current_user: User = Depends(require_hr_or_above)):
    return onboarding_progress_service.update_instance_status(db, current_user.organization_id, instance_id, data.status)


@router.patch("/instances/{instance_id}/tasks/{task_id}", response_model=OnboardingInstanceResponse)
def tasks_update_status(instance_id: UUID, task_id: UUID, data: OnboardingTaskStatusUpdate,
                        db: Session = Depends(get_db), current_user: User = Depends(require_hr_or_above)):
    return onboarding_progress_service.update_task_status(
        db, current_user.organization_id, instance_id, task_id, data.status
    )
