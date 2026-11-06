import uuid
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from fastapi import HTTPException
from app.models.models import (
    TrainingCourse, TrainingAssignment, TrainingLesson, TrainingLessonProgress,
    TrainingCertificate, Employee, User, TaskStatus,
)


def _course_query(db: Session, organization_id):
    return db.query(TrainingCourse).options(joinedload(TrainingCourse.lessons)).filter(
        TrainingCourse.organization_id == organization_id
    )


def list_courses(db: Session, organization_id, include_unpublished=False):
    query = _course_query(db, organization_id)
    if not include_unpublished:
        query = query.filter(TrainingCourse.published.is_(True))
    return query.order_by(TrainingCourse.created_at.desc()).all()


def create_course(db: Session, organization_id, actor_id, payload):
    data = payload.model_dump(exclude={"lessons"})
    course = TrainingCourse(**data, organization_id=organization_id, created_by=actor_id)
    for index, lesson_data in enumerate(payload.lessons):
        lesson = TrainingLesson(**lesson_data.model_dump(), order_index=lesson_data.order_index if lesson_data.order_index else index)
        course.lessons.append(lesson)
    db.add(course)
    db.commit()
    db.refresh(course)
    return course


def update_course(db: Session, organization_id, course_id, payload):
    course = db.query(TrainingCourse).filter_by(id=course_id, organization_id=organization_id).first()
    if not course:
        raise HTTPException(404, "Training course not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(course, key, value)
    course.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(course)
    return course


def replace_lessons(db: Session, organization_id, course_id, lessons):
    course = db.query(TrainingCourse).filter_by(id=course_id, organization_id=organization_id).first()
    if not course:
        raise HTTPException(404, "Training course not found")
    if db.query(TrainingAssignment).filter_by(course_id=course_id).filter(TrainingAssignment.progress_percentage > 0).count():
        raise HTTPException(409, "Lessons cannot be replaced after learners have started this course")
    course.lessons.clear()
    for index, item in enumerate(lessons):
        course.lessons.append(TrainingLesson(**item.model_dump(), order_index=item.order_index if item.order_index else index))
    db.commit()
    db.refresh(course)
    return course


def assign_course(db: Session, organization_id, course_id, employee_ids, actor_id, due_date):
    course = db.query(TrainingCourse).filter_by(id=course_id, organization_id=organization_id).first()
    if not course:
        raise HTTPException(404, "Training course not found")
    if not course.published:
        raise HTTPException(409, "Publish the course before assigning it")
    employees = db.query(Employee).filter(Employee.organization_id == organization_id, Employee.id.in_(employee_ids)).all()
    found = {employee.id for employee in employees}
    missing = set(employee_ids) - found
    if missing:
        raise HTTPException(404, "One or more employees were not found in this organization")
    existing = {row.employee_id for row in db.query(TrainingAssignment).filter(
        TrainingAssignment.course_id == course_id, TrainingAssignment.employee_id.in_(employee_ids)
    ).all()}
    created = []
    for employee in employees:
        if employee.id in existing:
            continue
        assignment = TrainingAssignment(course_id=course_id, employee_id=employee.id, assigned_by=actor_id, due_date=due_date)
        db.add(assignment)
        created.append(assignment)
    db.commit()
    for row in created:
        db.refresh(row)
    return created


def _assignment_payload(db, assignment):
    course = assignment.course
    employee = assignment.employee
    completed = db.query(TrainingLessonProgress).filter_by(assignment_id=assignment.id, is_completed=True).count()
    total = db.query(TrainingLesson).filter_by(course_id=course.id).count()
    return {
        "id": assignment.id, "course_id": course.id, "course_title": course.title,
        "employee_id": employee.id, "employee_name": employee.user.full_name,
        "status": assignment.status.value if hasattr(assignment.status, "value") else assignment.status,
        "progress_percentage": assignment.progress_percentage or 0,
        "due_date": assignment.due_date, "completed_at": assignment.completed_at,
        "certificate_code": assignment.certificate_code,
        "lessons_completed": completed, "lessons_total": total,
    }


def list_assignments(db: Session, organization_id, employee_id=None):
    query = db.query(TrainingAssignment).join(TrainingCourse).options(
        joinedload(TrainingAssignment.course), joinedload(TrainingAssignment.employee).joinedload(Employee.user)
    ).filter(TrainingCourse.organization_id == organization_id)
    if employee_id:
        query = query.filter(TrainingAssignment.employee_id == employee_id)
    rows = query.order_by(TrainingAssignment.assigned_at.desc()).all()
    return [_assignment_payload(db, row) for row in rows]


def list_my_assignments(db: Session, user: User):
    employee = db.query(Employee).filter_by(user_id=user.id, organization_id=user.organization_id).first()
    if not employee:
        return []
    rows = db.query(TrainingAssignment).join(TrainingCourse).options(
        joinedload(TrainingAssignment.course).joinedload(TrainingCourse.lessons),
        joinedload(TrainingAssignment.employee).joinedload(Employee.user),
    ).filter(TrainingCourse.organization_id == user.organization_id, TrainingAssignment.employee_id == employee.id).all()
    return [_assignment_payload(db, row) for row in rows]


def get_learning_item(db: Session, user: User, assignment_id):
    assignment = db.query(TrainingAssignment).join(TrainingCourse).options(
        joinedload(TrainingAssignment.course).joinedload(TrainingCourse.lessons),
        joinedload(TrainingAssignment.employee),
    ).filter(TrainingAssignment.id == assignment_id, TrainingCourse.organization_id == user.organization_id).first()
    if not assignment:
        raise HTTPException(404, "Training assignment not found")
    if user.role.value == "EMPLOYEE" and assignment.employee.user_id != user.id:
        raise HTTPException(403, "This training is assigned to another employee")
    assignment.last_accessed_at = datetime.utcnow()
    db.commit()
    progress = {row.lesson_id: row.is_completed for row in db.query(TrainingLessonProgress).filter_by(assignment_id=assignment.id).all()}
    result = _assignment_payload(db, assignment)
    result["lessons"] = [{
        "id": lesson.id, "title": lesson.title, "description": lesson.description,
        "content": lesson.content, "resource_url": lesson.resource_url,
        "duration_minutes": lesson.duration_minutes, "order_index": lesson.order_index,
        "is_preview": lesson.is_preview, "completed": progress.get(lesson.id, False),
    } for lesson in assignment.course.lessons]
    return result


def update_lesson_progress(db: Session, user: User, assignment_id, lesson_id, completed):
    assignment = db.query(TrainingAssignment).join(TrainingCourse).options(
        joinedload(TrainingAssignment.course), joinedload(TrainingAssignment.employee)
    ).filter(TrainingAssignment.id == assignment_id, TrainingCourse.organization_id == user.organization_id).first()
    if not assignment:
        raise HTTPException(404, "Training assignment not found")
    if assignment.employee.user_id != user.id:
        raise HTTPException(403, "Only the assigned employee can update lesson progress")
    lesson = db.query(TrainingLesson).filter_by(id=lesson_id, course_id=assignment.course_id).first()
    if not lesson:
        raise HTTPException(404, "Lesson not found in this course")
    progress = db.query(TrainingLessonProgress).filter_by(assignment_id=assignment.id, lesson_id=lesson.id).first()
    if not progress:
        progress = TrainingLessonProgress(assignment_id=assignment.id, lesson_id=lesson.id)
        db.add(progress)
    progress.is_completed = completed
    progress.completed_at = datetime.utcnow() if completed else None
    db.flush()
    total = db.query(TrainingLesson).filter_by(course_id=assignment.course_id).count()
    done = db.query(TrainingLessonProgress).filter_by(assignment_id=assignment.id, is_completed=True).count()
    assignment.progress_percentage = round((done / total) * 100, 2) if total else 0
    assignment.status = TaskStatus.COMPLETED if total and done == total else (TaskStatus.IN_PROGRESS if done else TaskStatus.PENDING)
    if assignment.status == TaskStatus.COMPLETED:
        assignment.completed_at = datetime.utcnow()
        if not db.query(TrainingCertificate).filter_by(assignment_id=assignment.id).first():
            code = f"ONX-{uuid.uuid4().hex[:12].upper()}"
            certificate = TrainingCertificate(
                assignment_id=assignment.id, organization_id=user.organization_id,
                employee_id=assignment.employee_id, course_title=assignment.course.title,
                certificate_code=code,
            )
            db.add(certificate)
            assignment.certificate_code = code
    else:
        assignment.completed_at = None
        if assignment.certificate_code:
            db.query(TrainingCertificate).filter_by(assignment_id=assignment.id).delete()
            assignment.certificate_code = None
    db.commit()
    db.refresh(assignment)
    return _assignment_payload(db, assignment)


def list_certificates(db: Session, user: User):
    query = db.query(TrainingCertificate).filter_by(organization_id=user.organization_id)
    if user.role.value == "EMPLOYEE":
        employee = db.query(Employee).filter_by(user_id=user.id, organization_id=user.organization_id).first()
        if not employee:
            return []
        query = query.filter_by(employee_id=employee.id)
    return query.order_by(TrainingCertificate.issued_at.desc()).all()


def analytics(db: Session, organization_id):
    courses = db.query(TrainingCourse).filter_by(organization_id=organization_id).count()
    assignments = db.query(TrainingAssignment).join(TrainingCourse).filter(TrainingCourse.organization_id == organization_id).all()
    total = len(assignments)
    completed = sum(1 for item in assignments if item.status == TaskStatus.COMPLETED)
    overdue = sum(1 for item in assignments if item.due_date and item.due_date < datetime.utcnow() and item.status != TaskStatus.COMPLETED)
    average = round(sum(item.progress_percentage or 0 for item in assignments) / total, 1) if total else 0
    return {"courses": courses, "assignments": total, "completed": completed, "overdue": overdue, "completion_rate": round(completed / total * 100, 1) if total else 0, "average_progress": average}
