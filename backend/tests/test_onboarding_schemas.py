import pytest
from pydantic import ValidationError
from app.schemas.onboarding import OnboardingStageInput, OnboardingTemplateCreate, OnboardingStatusUpdate
from app.models.models import OnboardingStatus


def test_template_accepts_ordered_stages():
    payload = OnboardingTemplateCreate(name="New Hire", stages=[
        OnboardingStageInput(name="Orientation", order_index=1, duration_days=1),
        OnboardingStageInput(name="Equipment", order_index=2),
    ])
    assert len(payload.stages) == 2
    assert payload.stages[0].name == "Orientation"


def test_template_rejects_blank_stage_name():
    with pytest.raises(ValidationError):
        OnboardingStageInput(name="  ")


def test_status_update_accepts_on_hold():
    payload = OnboardingStatusUpdate(status=OnboardingStatus.ON_HOLD)
    assert payload.status == OnboardingStatus.ON_HOLD
