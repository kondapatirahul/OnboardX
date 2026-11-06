from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.deps import get_current_user, require_hr_or_above, require_manager_or_above
from app.db.session import get_db
from app.models.models import User
from app.schemas.performance import GoalCreate, GoalUpdate, KeyResultUpdate, CycleCreate, SelfReviewInput, ManagerReviewInput, FeedbackCreate, ImprovementPlanCreate
from app.services import performance_service as service

router = APIRouter()

@router.get("/goals")
def goals(employee_id: UUID | None = None, goal_status: str | None = None, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return service.list_goals(db, user, employee_id, goal_status)

@router.post("/goals", status_code=status.HTTP_201_CREATED)
def goal_create(data: GoalCreate, db: Session = Depends(get_db), user: User = Depends(require_manager_or_above)):
    return service.create_goal(db, user, data)

@router.patch("/goals/{goal_id}")
def goal_update(goal_id: UUID, data: GoalUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return service.update_goal(db, user, goal_id, data)

@router.patch("/key-results/{key_id}")
def key_result_update(key_id: UUID, data: KeyResultUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return service.update_key_result(db, user, key_id, data.current_value)

@router.get("/cycles")
def cycles(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return service.list_cycles(db, user)

@router.post("/cycles", status_code=status.HTTP_201_CREATED)
def cycle_create(data: CycleCreate, db: Session = Depends(get_db), user: User = Depends(require_hr_or_above)):
    return service.create_cycle(db, user, data)

@router.post("/cycles/{cycle_id}/reviews", status_code=status.HTTP_201_CREATED)
def review_create(cycle_id: UUID, employee_id: UUID, db: Session = Depends(get_db), user: User = Depends(require_manager_or_above)):
    return service.create_review(db, user, cycle_id, employee_id)

@router.get("/reviews")
def reviews(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return service.list_reviews(db, user)

@router.patch("/reviews/{review_id}/self")
def self_review(review_id: UUID, data: SelfReviewInput, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return service.submit_self_review(db, user, review_id, data)

@router.patch("/reviews/{review_id}/manager")
def manager_review(review_id: UUID, data: ManagerReviewInput, db: Session = Depends(get_db), user: User = Depends(require_manager_or_above)):
    return service.submit_manager_review(db, user, review_id, data)

@router.post("/reviews/{review_id}/feedback", status_code=status.HTTP_201_CREATED)
def feedback(review_id: UUID, data: FeedbackCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return service.add_feedback(db, user, review_id, data)

@router.get("/improvement-plans")
def improvement_plans(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return service.list_improvement_plans(db, user)

@router.post("/improvement-plans", status_code=status.HTTP_201_CREATED)
def improvement_plan_create(data: ImprovementPlanCreate, db: Session = Depends(get_db), user: User = Depends(require_manager_or_above)):
    return service.create_improvement_plan(db, user, data)

@router.get("/analytics")
def performance_analytics(db: Session = Depends(get_db), user: User = Depends(require_hr_or_above)):
    return service.analytics(db, user)

@router.get("/team")
def team_members(db: Session = Depends(get_db), user: User = Depends(require_manager_or_above)):
    if user.role.value in ("HR_ADMIN", "SUPER_ADMIN"):
        from app.models.models import Employee as EmployeeModel
        from app.models.models import User as UserModel
        rows = db.query(EmployeeModel, UserModel).join(UserModel, UserModel.id == EmployeeModel.user_id).filter(EmployeeModel.organization_id == user.organization_id).order_by(UserModel.full_name.asc()).limit(500).all()
        return [{"id": employee.id, "employee_id": employee.employee_id, "full_name": account.full_name, "email": account.email, "designation": employee.designation} for employee, account in rows]
    return service.list_team_members(db, user)
