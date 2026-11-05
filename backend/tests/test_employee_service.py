from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.services import employee_service


def test_list_employees_returns_pagination_metadata(monkeypatch):
    organization_id = uuid4()
    monkeypatch.setattr(employee_service.repository, "count_employees", lambda *args: 41)
    monkeypatch.setattr(employee_service.repository, "search_employees", lambda *args, **kwargs: [])

    result = employee_service.list_employees(
        db=object(),
        organization_id=organization_id,
        page=2,
        page_size=20,
    )

    assert result == {
        "items": [],
        "total": 41,
        "page": 2,
        "page_size": 20,
        "pages": 3,
    }


def test_list_employees_requires_organization():
    with pytest.raises(HTTPException) as error:
        employee_service.list_employees(object(), None)
    assert error.value.status_code == 400


def test_get_employee_hides_records_outside_organization(monkeypatch):
    monkeypatch.setattr(employee_service.repository, "get_employee", lambda *args: None)

    with pytest.raises(HTTPException) as error:
        employee_service.get_employee(object(), uuid4(), uuid4())
    assert error.value.status_code == 404
