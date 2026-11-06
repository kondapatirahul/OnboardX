from sqlalchemy.orm import Session, joinedload
from app.models.models import (
    Employee, OnboardingInstance, OnboardingStage, OnboardingTask,
    OnboardingTemplate, TaskPriority, TaskStatus, OnboardingStatus,
)


def list_templates(db: Session, organization_id):
    return (db.query(OnboardingTemplate)
            .options(joinedload(OnboardingTemplate.stages))
            .filter(OnboardingTemplate.organization_id == organization_id)
            .order_by(OnboardingTemplate.created_at.desc()).all())


def get_template(db: Session, organization_id, template_id):
    return (db.query(OnboardingTemplate)
            .options(joinedload(OnboardingTemplate.stages))
            .filter(OnboardingTemplate.organization_id == organization_id,
                    OnboardingTemplate.id == template_id).first())


def create_template(db: Session, organization_id, user_id, data):
    template = OnboardingTemplate(name=data.name, description=data.description,
                                  organization_id=organization_id, created_by=user_id)
    for stage in data.stages:
        template.stages.append(OnboardingStage(**stage.model_dump()))
    db.add(template)
    db.commit()
    db.refresh(template)
    return template


def get_employee(db: Session, organization_id, employee_id):
    return (db.query(Employee).filter(Employee.organization_id == organization_id,
                                      Employee.id == employee_id).first())


def create_instance(db: Session, organization_id, employee, template):
    instance = OnboardingInstance(employee_id=employee.id, template_id=template.id,
                                  organization_id=organization_id,
                                  status=OnboardingStatus.IN_PROGRESS, progress_percentage=0)
    db.add(instance)
    db.flush()
    for stage in sorted(template.stages, key=lambda item: item.order_index):
        db.add(OnboardingTask(
            instance_id=instance.id, stage_id=stage.id, organization_id=organization_id,
            title=stage.name, description=stage.description,
            assigned_to=employee.user_id, status=TaskStatus.PENDING,
            priority=TaskPriority.MEDIUM,
        ))
    db.commit()
    return get_instance(db, organization_id, instance.id)


def get_instance(db: Session, organization_id, instance_id):
    return (db.query(OnboardingInstance)
            .options(joinedload(OnboardingInstance.tasks))
            .filter(OnboardingInstance.organization_id == organization_id,
                    OnboardingInstance.id == instance_id).first())


def list_instances(db: Session, organization_id, employee_id=None):
    query = (db.query(OnboardingInstance)
             .options(joinedload(OnboardingInstance.tasks))
             .filter(OnboardingInstance.organization_id == organization_id))
    if employee_id:
        query = query.filter(OnboardingInstance.employee_id == employee_id)
    return query.order_by(OnboardingInstance.created_at.desc()).all()


def update_instance_status(db: Session, instance, status):
    instance.status = status
    db.commit()
    return get_instance(db, instance.organization_id, instance.id)


def get_task(db: Session, organization_id, instance_id, task_id):
    return (db.query(OnboardingTask)
            .join(OnboardingInstance, OnboardingTask.instance_id == OnboardingInstance.id)
            .filter(OnboardingTask.id == task_id,
                    OnboardingTask.organization_id == organization_id,
                    OnboardingInstance.organization_id == organization_id,
                    OnboardingInstance.id == instance_id).first())
