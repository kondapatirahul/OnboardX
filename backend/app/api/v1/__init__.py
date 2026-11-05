from fastapi import APIRouter
from app.api.v1 import health, auth, dashboard, employees, departments, profile

router = APIRouter()
router.include_router(health.router, prefix="/health", tags=["health"])
router.include_router(auth.router, prefix="/auth", tags=["auth"])

router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])

router.include_router(employees.router, prefix="/employees", tags=["employees"])

router.include_router(departments.router, prefix="/departments", tags=["departments"])

router.include_router(profile.router, prefix="/profile", tags=["profile"])
