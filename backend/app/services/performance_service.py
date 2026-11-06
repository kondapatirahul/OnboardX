from datetime import datetime
from uuid import UUID
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.models import (
    Employee, PerformanceGoal, PerformanceKeyResult, PerformanceReviewCycle,
    PerformanceReview, PerformanceFeedback, PerformanceImprovementPlan, User,
)


def _employee_for_user(db: Session, user: User):
    return db.query(Employee).filter(Employee.user_id == user.id, Employee.organization_id == user.organization_id).first()


def _assert_employee_scope(db: Session, user: User, employee_id: UUID, allow_hr=True):
    employee = db.query(Employee).filter(Employee.id == employee_id, Employee.organization_id == user.organization_id).first()
    if not employee:
        raise HTTPException(404, "Employee not found")
    if user.role.value in ("HR_ADMIN", "SUPER_ADMIN") and allow_hr:
        return employee
    actor = _employee_for_user(db, user)
    if not actor or (actor.id != employee.id and employee.manager_id != actor.id):
        raise HTTPException(403, "You can only access your own records or your direct reports")
    return employee


def list_goals(db: Session, user: User, employee_id=None, status=None):
    query = db.query(PerformanceGoal, Employee, User).join(Employee, Employee.id == PerformanceGoal.owner_id).join(User, User.id == Employee.user_id).filter(PerformanceGoal.organization_id == user.organization_id)
    if user.role.value == "EMPLOYEE":
        actor = _employee_for_user(db, user)
        if not actor:
            return []
        query = query.filter(PerformanceGoal.owner_id == actor.id)
    elif user.role.value == "MANAGER":
        actor = _employee_for_user(db, user)
        if not actor:
            return []
        query = query.filter((PerformanceGoal.owner_id == actor.id) | (Employee.manager_id == actor.id))
    elif employee_id:
        query = query.filter(PerformanceGoal.owner_id == employee_id)
    if status:
        query = query.filter(PerformanceGoal.status == status)
    rows = query.order_by(PerformanceGoal.created_at.desc()).all()
    output = []
    for goal, employee, owner_user in rows:
        keys = db.query(PerformanceKeyResult).filter(PerformanceKeyResult.goal_id == goal.id).order_by(PerformanceKeyResult.order_index).all()
        weighted = sum(max(0, min(100, ((k.current_value-k.start_value)/(k.target_value-k.start_value))*100)) * k.weight for k in keys)
        weight = sum(k.weight for k in keys)
        progress = round(weighted / weight) if weight else goal.progress
        output.append({"id": goal.id, "owner_id": goal.owner_id, "employee_name": owner_user.full_name, "title": goal.title, "description": goal.description, "goal_type": goal.goal_type, "status": goal.status, "priority": goal.priority, "progress": progress, "start_date": goal.start_date, "due_date": goal.due_date, "created_at": goal.created_at, "key_results": [{"id": k.id, "title": k.title, "metric": k.metric, "start_value": k.start_value, "target_value": k.target_value, "current_value": k.current_value, "weight": k.weight, "progress": round(max(0, min(100, ((k.current_value-k.start_value)/(k.target_value-k.start_value))*100)))} for k in keys]})
    return output


def create_goal(db: Session, user: User, data):
    _assert_employee_scope(db, user, data.owner_id)
    if data.due_date and data.start_date and data.due_date < data.start_date:
        raise HTTPException(422, "Due date must not precede start date")
    goal = PerformanceGoal(organization_id=user.organization_id, owner_id=data.owner_id, created_by=user.id, title=data.title.strip(), description=data.description, goal_type=data.goal_type, priority=data.priority, start_date=data.start_date, due_date=data.due_date)
    db.add(goal); db.flush()
    for item in data.key_results:
        db.add(PerformanceKeyResult(goal_id=goal.id, **item.model_dump()))
    db.commit(); db.refresh(goal)
    return goal


def update_goal(db: Session, user: User, goal_id: UUID, data):
    goal = db.query(PerformanceGoal).filter(PerformanceGoal.id == goal_id, PerformanceGoal.organization_id == user.organization_id).first()
    if not goal:
        raise HTTPException(404, "Goal not found")
    _assert_employee_scope(db, user, goal.owner_id)
    values = data.model_dump(exclude_unset=True)
    if values.get("status") not in (None, "not_started", "in_progress", "at_risk", "completed", "cancelled"):
        raise HTTPException(422, "Invalid goal status")
    if values.get("priority") not in (None, "low", "medium", "high", "critical"):
        raise HTTPException(422, "Invalid priority")
    for key, value in values.items():
        setattr(goal, key, value)
    if goal.status == "completed":
        goal.progress = 100; goal.completed_at = datetime.utcnow()
    elif goal.status in ("in_progress", "at_risk") and goal.progress == 0:
        goal.progress = 1
    goal.updated_at = datetime.utcnow(); db.commit(); db.refresh(goal)
    return goal


def update_key_result(db: Session, user: User, key_id: UUID, current_value: float):
    key = db.query(PerformanceKeyResult).join(PerformanceGoal).filter(PerformanceKeyResult.id == key_id, PerformanceGoal.organization_id == user.organization_id).first()
    if not key:
        raise HTTPException(404, "Key result not found")
    _assert_employee_scope(db, user, key.goal.owner_id)
    key.current_value = current_value; key.updated_at = datetime.utcnow()
    goal = key.goal
    keys = db.query(PerformanceKeyResult).filter(PerformanceKeyResult.goal_id == goal.id).all()
    weight = sum(item.weight for item in keys)
    if weight:
        goal.progress = round(sum(max(0, min(100, ((item.current_value-item.start_value)/(item.target_value-item.start_value))*100)) * item.weight for item in keys) / weight)
    if goal.progress >= 100:
        goal.status = "completed"; goal.completed_at = datetime.utcnow()
    elif goal.status == "not_started":
        goal.status = "in_progress"
    db.commit(); return {"id": key.id, "current_value": key.current_value, "goal_progress": goal.progress}


def create_cycle(db: Session, user: User, data):
    row = PerformanceReviewCycle(organization_id=user.organization_id, created_by=user.id, **data.model_dump())
    db.add(row); db.commit(); db.refresh(row); return row


def list_cycles(db: Session, user: User):
    return db.query(PerformanceReviewCycle).filter(PerformanceReviewCycle.organization_id == user.organization_id).order_by(PerformanceReviewCycle.starts_at.desc()).all()


def create_review(db: Session, user: User, cycle_id: UUID, employee_id: UUID):
    employee = _assert_employee_scope(db, user, employee_id)
    cycle = db.query(PerformanceReviewCycle).filter(PerformanceReviewCycle.id == cycle_id, PerformanceReviewCycle.organization_id == user.organization_id).first()
    if not cycle: raise HTTPException(404, "Review cycle not found")
    row = db.query(PerformanceReview).filter(PerformanceReview.cycle_id == cycle.id, PerformanceReview.employee_id == employee.id).first()
    if row: raise HTTPException(409, "A review already exists for this employee in the cycle")
    row = PerformanceReview(organization_id=user.organization_id, cycle_id=cycle.id, employee_id=employee.id, manager_id=employee.manager_id)
    db.add(row); db.commit(); db.refresh(row); return row


def list_reviews(db: Session, user: User):
    query = db.query(PerformanceReview, Employee, User).join(Employee, Employee.id == PerformanceReview.employee_id).join(User, User.id == Employee.user_id).filter(PerformanceReview.organization_id == user.organization_id)
    if user.role.value == "EMPLOYEE":
        actor = _employee_for_user(db, user)
        query = query.filter(PerformanceReview.employee_id == actor.id if actor else False)
    elif user.role.value == "MANAGER":
        actor = _employee_for_user(db, user)
        query = query.filter((PerformanceReview.employee_id == actor.id) | (PerformanceReview.manager_id == actor.id))
    return [{"id": r.id, "cycle_id": r.cycle_id, "employee_id": r.employee_id, "employee_name": u.full_name, "manager_id": r.manager_id, "self_rating": r.self_rating, "manager_rating": r.manager_rating, "self_summary": r.self_summary, "manager_summary": r.manager_summary, "strengths": r.strengths, "growth_areas": r.growth_areas, "status": r.status, "submitted_at": r.submitted_at, "reviewed_at": r.reviewed_at} for r, e, u in query.order_by(PerformanceReview.created_at.desc()).all()]


def submit_self_review(db: Session, user: User, review_id: UUID, data):
    actor = _employee_for_user(db, user)
    row = db.query(PerformanceReview).filter(PerformanceReview.id == review_id, PerformanceReview.organization_id == user.organization_id).first()
    if not row: raise HTTPException(404, "Review not found")
    if not actor or row.employee_id != actor.id: raise HTTPException(403, "Only the review subject can submit a self-review")
    row.self_rating = data.self_rating; row.self_summary = data.self_summary; row.submitted_at = datetime.utcnow(); row.status = "self_submitted"
    db.commit(); db.refresh(row); return row


def submit_manager_review(db: Session, user: User, review_id: UUID, data):
    row = db.query(PerformanceReview).filter(PerformanceReview.id == review_id, PerformanceReview.organization_id == user.organization_id).first()
    if not row: raise HTTPException(404, "Review not found")
    _assert_employee_scope(db, user, row.employee_id)
    if row.manager_id is None or _employee_for_user(db, user) is None or row.manager_id != _employee_for_user(db, user).id:
        if user.role.value not in ("HR_ADMIN", "SUPER_ADMIN"): raise HTTPException(403, "Only the assigned manager or HR can submit this review")
    row.manager_rating = data.manager_rating; row.manager_summary = data.manager_summary; row.strengths = data.strengths; row.growth_areas = data.growth_areas; row.reviewed_at = datetime.utcnow(); row.status = "completed"
    db.commit(); db.refresh(row); return row


def add_feedback(db: Session, user: User, review_id: UUID, data):
    row = db.query(PerformanceReview).filter(PerformanceReview.id == review_id, PerformanceReview.organization_id == user.organization_id).first()
    if not row: raise HTTPException(404, "Review not found")
    if user.role.value == "EMPLOYEE":
        actor = _employee_for_user(db, user)
        if not actor or (actor.id != row.employee_id and actor.id != row.manager_id):
            raise HTTPException(403, "You are not a participant in this review")
    if data.feedback_type not in ("peer", "manager", "self"): raise HTTPException(422, "Invalid feedback type")
    feedback = PerformanceFeedback(organization_id=user.organization_id, review_id=row.id, author_id=None if data.is_anonymous else user.id, **data.model_dump())
    db.add(feedback); db.commit(); db.refresh(feedback); return {"id": feedback.id, "feedback_type": feedback.feedback_type, "rating": feedback.rating, "strengths": feedback.strengths, "suggestions": feedback.suggestions, "is_anonymous": feedback.is_anonymous, "created_at": feedback.created_at}


def create_improvement_plan(db: Session, user: User, data):
    _assert_employee_scope(db, user, data.employee_id)
    if data.ends_at <= data.starts_at: raise HTTPException(422, "Plan end must be after start")
    payload = data.model_dump()
    row = PerformanceImprovementPlan(organization_id=user.organization_id, created_by=user.id, **payload)
    db.add(row); db.commit(); db.refresh(row); return row


def list_improvement_plans(db: Session, user: User):
    query = db.query(PerformanceImprovementPlan, Employee, User).join(Employee, Employee.id == PerformanceImprovementPlan.employee_id).join(User, User.id == Employee.user_id).filter(PerformanceImprovementPlan.organization_id == user.organization_id)
    if user.role.value == "EMPLOYEE":
        actor = _employee_for_user(db, user); query = query.filter(PerformanceImprovementPlan.employee_id == actor.id if actor else False)
    elif user.role.value == "MANAGER":
        actor = _employee_for_user(db, user); query = query.filter(Employee.manager_id == actor.id if actor else False)
    return [{"id": p.id, "employee_id": p.employee_id, "employee_name": u.full_name, "review_id": p.review_id, "title": p.title, "objectives": p.objectives, "support_plan": p.support_plan, "status": p.status, "starts_at": p.starts_at, "ends_at": p.ends_at, "outcome_notes": p.outcome_notes} for p, e, u in query.order_by(PerformanceImprovementPlan.created_at.desc()).all()]


def analytics(db: Session, user: User):
    goals = db.query(PerformanceGoal).filter(PerformanceGoal.organization_id == user.organization_id).all()
    reviews = db.query(PerformanceReview).filter(PerformanceReview.organization_id == user.organization_id).all()
    plans = db.query(PerformanceImprovementPlan).filter(PerformanceImprovementPlan.organization_id == user.organization_id).all()
    completed = sum(1 for goal in goals if goal.status == "completed")
    return {"goals": len(goals), "goals_completed": completed, "goal_completion_rate": round(completed / len(goals) * 100) if goals else 0, "reviews": len(reviews), "reviews_completed": sum(1 for review in reviews if review.status == "completed"), "reviews_pending": sum(1 for review in reviews if review.status != "completed"), "average_manager_rating": round(sum(r.manager_rating for r in reviews if r.manager_rating is not None) / max(1, sum(1 for r in reviews if r.manager_rating is not None)), 2), "active_improvement_plans": sum(1 for plan in plans if plan.status == "active"), "at_risk_goals": sum(1 for goal in goals if goal.status == "at_risk")}


def list_team_members(db: Session, user: User):
    actor = _employee_for_user(db, user)
    if not actor:
        return []
    rows = db.query(Employee, User).join(User, User.id == Employee.user_id).filter(
        Employee.organization_id == user.organization_id,
        Employee.manager_id == actor.id,
    ).order_by(User.full_name.asc()).all()
    return [{"id": employee.id, "employee_id": employee.employee_id, "full_name": account.full_name, "email": account.email, "designation": employee.designation} for employee, account in rows]
