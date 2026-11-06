from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.schemas.department import DepartmentCreate, DepartmentUpdate
from app.services import department_service


def test_list_departments_returns_serialized_items(monkeypatch):
    department = type("DepartmentRow", (), {
        "id": uuid4(), "name": "Engineering", "organization_id": uuid4(), "created_at": None
    })()
    monkeypatch.setattr(department_service.repository, "list_departments", lambda *args: [(department, 4)])

    result = department_service.list_departments(object(), department.organization_id)

    assert result["total"] == 1
    assert result["items"][0]["name"] == "Engineering"
    assert result["items"][0]["employee_count"] == 4


def test_list_departments_requires_organization():
    with pytest.raises(HTTPException) as error:
        department_service.list_departments(object(), None)
    assert error.value.status_code == 400


def test_create_department_rejects_duplicate_name(monkeypatch):
    monkeypatch.setattr(department_service.repository, "get_department_by_name", lambda *args: object())
    with pytest.raises(HTTPException) as error:
        department_service.create_department(object(), uuid4(), DepartmentCreate(name="Engineering"))
    assert error.value.status_code == 409


def test_update_department_rejects_unknown_department(monkeypatch):
    monkeypatch.setattr(department_service.repository, "get_department", lambda *args: None)
    with pytest.raises(HTTPException) as error:
        department_service.update_department(object(), uuid4(), uuid4(), DepartmentUpdate(name="People"))
    assert error.value.status_code == 404


def test_delete_department_blocks_assigned_employees(monkeypatch):
    department = type("Department", (), {"id": uuid4()})()
    monkeypatch.setattr(department_service.repository, "get_department", lambda *args: department)
    monkeypatch.setattr(department_service.repository, "count_department_employees", lambda *args: 2)
    with pytest.raises(HTTPException) as error:
        department_service.delete_department(object(), uuid4(), department.id)
    assert error.value.status_code == 409
