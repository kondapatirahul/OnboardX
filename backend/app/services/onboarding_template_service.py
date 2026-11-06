from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.repositories import onboarding_repository as repository


def _require_org(organization_id):
    if not organization_id:
        raise HTTPException(status_code=400, detail="User is not associated with an organization")


def _template_data(template):
    return {"id": template.id, "name": template.name, "description": template.description,
            "is_active": template.is_active,
            "stages": sorted(template.stages, key=lambda stage: stage.order_index),
            "created_at": template.created_at}


def list_templates(db: Session, organization_id):
    _require_org(organization_id)
    items = repository.list_templates(db, organization_id)
    return {"items": [_template_data(item) for item in items], "total": len(items)}


def create_template(db: Session, organization_id, user_id, data):
    _require_org(organization_id)
    try:
        return _template_data(repository.create_template(db, organization_id, user_id, data))
    except Exception:
        db.rollback()
        raise


def update_template(db: Session, organization_id, template_id, data):
    _require_org(organization_id)
    template = repository.get_template(db, organization_id, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Onboarding template not found")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(template, key, value)
    db.commit()
    db.refresh(template)
    return _template_data(template)
