import pytest
from pydantic import ValidationError

from app.schemas.dashboard import DashboardStats, DepartmentSummary


def test_dashboard_stats_accepts_valid_metrics():
    result = DashboardStats(
        total_employees=12,
        active_onboarding=4,
        pending_approvals=2,
        completed_onboarding=6,
        completion_percentage=60.0,
    )
    assert result.total_employees == 12
    assert result.completion_percentage == 60.0


def test_dashboard_stats_rejects_negative_counts():
    with pytest.raises(ValidationError):
        DashboardStats(
            total_employees=-1,
            active_onboarding=0,
            pending_approvals=0,
            completed_onboarding=0,
            completion_percentage=0,
        )


def test_department_summary_serializes_department_id():
    result = DepartmentSummary(
        department_id="department-1",
        department_name="Engineering",
        employee_count=5,
    )
    assert result.model_dump()["department_name"] == "Engineering"
