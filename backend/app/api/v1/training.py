from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.deps import get_current_user, require_hr_or_above
from app.db.session import get_db
from app.models.models import User
from app.schemas.training import (
    TrainingCourseCreate, TrainingCourseUpdate, TrainingLessonInput,
    TrainingAssignmentCreate, TrainingProgressUpdate, TrainingCourseResponse,
)
from app.services import training_service

router = APIRouter()


@router.get("/courses", response_model=list[TrainingCourseResponse])
def courses_list(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    can_manage = current_user.role.value in ("HR_ADMIN", "SUPER_ADMIN")
    return training_service.list_courses(db, current_user.organization_id, include_unpublished=can_manage)


@router.post("/courses", response_model=TrainingCourseResponse, status_code=status.HTTP_201_CREATED)
def courses_create(data: TrainingCourseCreate, db: Session = Depends(get_db), current_user: User = Depends(require_hr_or_above)):
    return training_service.create_course(db, current_user.organization_id, current_user.id, data)


@router.patch("/courses/{course_id}", response_model=TrainingCourseResponse)
def courses_update(course_id: UUID, data: TrainingCourseUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_hr_or_above)):
    return training_service.update_course(db, current_user.organization_id, course_id, data)


@router.put("/courses/{course_id}/lessons", response_model=TrainingCourseResponse)
def lessons_replace(course_id: UUID, lessons: list[TrainingLessonInput], db: Session = Depends(get_db), current_user: User = Depends(require_hr_or_above)):
    return training_service.replace_lessons(db, current_user.organization_id, course_id, lessons)


@router.post("/courses/{course_id}/assignments", status_code=status.HTTP_201_CREATED)
def course_assign(course_id: UUID, data: TrainingAssignmentCreate, db: Session = Depends(get_db), current_user: User = Depends(require_hr_or_above)):
    rows = training_service.assign_course(db, current_user.organization_id, course_id, data.employee_ids, current_user.id, data.due_date)
    return {"created": len(rows), "message": f"Training assigned to {len(rows)} employee(s)."}


@router.get("/assignments")
def assignments_list(employee_id: UUID | None = None, db: Session = Depends(get_db), current_user: User = Depends(require_hr_or_above)):
    return training_service.list_assignments(db, current_user.organization_id, employee_id)


@router.get("/my-learning")
def my_learning(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return training_service.list_my_assignments(db, current_user)


@router.get("/assignments/{assignment_id}")
def learning_detail(assignment_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return training_service.get_learning_item(db, current_user, assignment_id)


@router.patch("/assignments/{assignment_id}/lessons/{lesson_id}")
def lesson_progress(assignment_id: UUID, lesson_id: UUID, data: TrainingProgressUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return training_service.update_lesson_progress(db, current_user, assignment_id, lesson_id, data.completed)


@router.get("/certificates")
def certificates_list(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return training_service.list_certificates(db, current_user)


@router.get("/analytics")
def training_analytics(db: Session = Depends(get_db), current_user: User = Depends(require_hr_or_above)):
    return training_service.analytics(db, current_user.organization_id)
