from types import SimpleNamespace
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.schemas.profile import ProfileUpdate
from app.models.models import UserRole
from app.services.profile_read_service import get_my_profile
from app.services.profile_update_service import update_my_profile


def make_user():
    return SimpleNamespace(id=uuid4(), organization_id=uuid4(), email="old@example.com", full_name="Old Name", role=UserRole.EMPLOYEE, is_active=True)


def make_row(user):
    employee = SimpleNamespace(
        employee_id="EMP-100", designation="QA Engineer", department_id=None,
        manager_id=None, joining_date=None, status="active", created_at=None, updated_at=None,
    )
    return (employee, user, None, None)


def test_get_my_profile_returns_employee_and_user_fields():
    user = make_user()
    with patch("app.services.profile_read_service.get_profile_record", return_value=make_row(user)):
        result = get_my_profile(MagicMock(), user)
    assert result["email"] == "old@example.com"
    assert result["employee_id"] == "EMP-100"


def test_get_my_profile_returns_404_when_profile_missing():
    user = make_user()
    with patch("app.services.profile_read_service.get_profile_record", return_value=None):
        with pytest.raises(HTTPException) as error:
            get_my_profile(MagicMock(), user)
    assert error.value.status_code == 404


def test_update_my_profile_updates_only_display_name():
    user = make_user()
    db = MagicMock()
    with patch("app.services.profile_update_service.get_profile_record", return_value=make_row(user)), patch(
        "app.services.profile_read_service.get_profile_record", return_value=make_row(user)
    ):
        result = update_my_profile(db, user, ProfileUpdate(full_name="New Name"))
    assert user.full_name == "New Name"
    assert user.email == "old@example.com"
    db.commit.assert_called_once()
    assert result["full_name"] == "New Name"
