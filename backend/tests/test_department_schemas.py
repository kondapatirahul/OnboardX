import pytest
from pydantic import ValidationError

from app.schemas.department import DepartmentCreate, DepartmentListResponse


def test_department_name_is_trimmed_and_internal_spaces_normalized():
    payload = DepartmentCreate(name="  Customer   Success  ")
    assert payload.name == "Customer Success"


def test_department_name_rejects_blank_value():
    with pytest.raises(ValidationError):
        DepartmentCreate(name="   ")


def test_department_list_response_accepts_empty_directory():
    result = DepartmentListResponse(items=[], total=0)
    assert result.items == []
    assert result.total == 0
