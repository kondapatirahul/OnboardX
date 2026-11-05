from fastapi import APIRouter
from app.api.v1 import profile_read, profile_update

router = APIRouter()
router.include_router(profile_read.router)
router.include_router(profile_update.router)
