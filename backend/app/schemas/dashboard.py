from pydantic import BaseModel, Field


class DashboardStats(BaseModel):
    total_employees: int = Field(ge=0)
    active_onboarding: int = Field(ge=0)
    pending_approvals: int = Field(ge=0)
    completed_onboarding: int = Field(ge=0)
    completion_percentage: float = Field(ge=0, le=100)


class DepartmentSummary(BaseModel):
    department_id: str
    department_name: str
    employee_count: int = Field(ge=0)
