from uuid import uuid4
import pytest
from fastapi import HTTPException
from app.schemas.onboarding import OnboardingTemplateCreate
from app.services import onboarding_assignment_service, onboarding_template_service


def test_list_templates_requires_organization():
    with pytest.raises(HTTPException) as error:
        onboarding_template_service.list_templates(object(), None)
    assert error.value.status_code == 400


def test_assign_template_rejects_employee_outside_organization(monkeypatch):
    monkeypatch.setattr(onboarding_assignment_service.repository, "get_employee", lambda *args: None)
    with pytest.raises(HTTPException) as error:
        onboarding_assignment_service.assign_template(object(), uuid4(), uuid4(), uuid4())
    assert error.value.status_code == 404


def test_assign_template_rejects_inactive_or_missing_template(monkeypatch):
    employee = type("Employee", (), {"id": uuid4()})()
    monkeypatch.setattr(onboarding_assignment_service.repository, "get_employee", lambda *args: employee)
    monkeypatch.setattr(onboarding_assignment_service.repository, "get_template", lambda *args: None)
    with pytest.raises(HTTPException) as error:
        onboarding_assignment_service.assign_template(object(), uuid4(), employee.id, uuid4())
    assert error.value.status_code == 404


def test_update_template_returns_not_found(monkeypatch):
    from app.schemas.onboarding import OnboardingTemplateUpdate
    monkeypatch.setattr(onboarding_assignment_service.repository, "get_template", lambda *args: None)
    with pytest.raises(HTTPException) as error:
        onboarding_template_service.update_template(object(), uuid4(), uuid4(), OnboardingTemplateUpdate(name="Updated"))
    assert error.value.status_code == 404
