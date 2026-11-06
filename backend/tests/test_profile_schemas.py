import pytest
from pydantic import ValidationError

from app.schemas.profile import ProfileUpdate


def test_profile_update_trims_full_name():
    payload = ProfileUpdate(full_name="  Rahul Kondapati  ")
    assert payload.full_name == "Rahul Kondapati"


def test_profile_update_rejects_blank_name():
    with pytest.raises(ValidationError):
        ProfileUpdate(full_name="   ")


def test_profile_update_does_not_allow_hr_controlled_fields():
    with pytest.raises(ValidationError):
        ProfileUpdate(status="inactive")
