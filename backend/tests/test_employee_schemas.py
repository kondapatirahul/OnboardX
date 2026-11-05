import pytest
from pydantic import ValidationError

from app.models.models import EmployeeStatus
from app.schemas.employee import EmployeeCreate, EmployeeListResponse, EmployeeUpdate


def test_employee_create_trims_required_fields():
    payload = EmployeeCreate(
        employee_id=" EMP-100 ",
        full_name=" Rahul Kumar ",
        email="rahul@example.com",
        temporary_password="temporary123",
    )
    assert payload.employee_id == "EMP-100"
    assert payload.full_name == "Rahul Kumar"
    assert payload.status == EmployeeStatus.ONBOARDING


def test_employee_create_rejects_short_temporary_password():
    with pytest.raises(ValidationError):
        EmployeeCreate(
            employee_id="EMP-101",
            full_name="Test User",
            email="test@example.com",
            temporary_password="short",
        )


def test_employee_update_rejects_blank_name():
    with pytest.raises(ValidationError):
        EmployeeUpdate(full_name="   ")


def test_employee_list_response_validates_pagination():
    result = EmployeeListResponse(items=[], total=0, page=1, page_size=20, pages=0)
    assert result.total == 0
    assert result.page_size == 20
