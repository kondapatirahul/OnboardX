from app.models.models import UserRole
from app.documents.enums import DocumentVisibility

HR_ROLES = {UserRole.HR_ADMIN, UserRole.SUPER_ADMIN}
MANAGEMENT_ROLES = {UserRole.MANAGER, UserRole.HR_ADMIN, UserRole.SUPER_ADMIN}


def is_hr(user) -> bool:
    return bool(user and user.role in HR_ROLES)


def is_manager_or_hr(user) -> bool:
    return bool(user and user.role in MANAGEMENT_ROLES)


def can_create_for_employee(user, employee) -> bool:
    if not user or not employee:
        return False
    if user.organization_id != employee.organization_id:
        return False
    if is_hr(user):
        return True
    return bool(employee.user_id == user.id)


def can_view_document(user, document, employee=None, grant=None) -> bool:
    if not user or not document or user.organization_id != document.organization_id:
        return False
    if is_hr(user):
        return True
    if grant and grant.is_active:
        return True
    if employee and employee.user_id == user.id:
        return document.visibility in {
            DocumentVisibility.PRIVATE.value,
            DocumentVisibility.EMPLOYEE_AND_HR.value,
            DocumentVisibility.ORGANIZATION.value,
        }
    if document.visibility == DocumentVisibility.ORGANIZATION.value:
        return True
    return False


def can_manage_document(user, document, employee=None) -> bool:
    if not user or not document or user.organization_id != document.organization_id:
        return False
    if is_hr(user):
        return True
    return bool(employee and employee.user_id == user.id and document.created_by == user.id)


def can_review_document(user) -> bool:
    return is_hr(user)


def can_download_document(user, document, employee=None, grant=None) -> bool:
    if not can_view_document(user, document, employee, grant):
        return False
    if grant and not is_hr(user) and grant.permission not in {"download", "manage"}:
        return False
    if document.lifecycle in {"quarantined", "deleted"}:
        return False
    if document.scan_status == "suspicious":
        return False
    return True
