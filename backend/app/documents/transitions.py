from app.documents.enums import DocumentLifecycle, ReviewDecision
from app.documents.errors import DocumentStateError

_ALLOWED = {
    DocumentLifecycle.DRAFT: {DocumentLifecycle.SUBMITTED, DocumentLifecycle.ARCHIVED},
    DocumentLifecycle.SUBMITTED: {DocumentLifecycle.IN_REVIEW, DocumentLifecycle.APPROVED, DocumentLifecycle.REJECTED, DocumentLifecycle.DRAFT},
    DocumentLifecycle.IN_REVIEW: {DocumentLifecycle.APPROVED, DocumentLifecycle.REJECTED, DocumentLifecycle.SUBMITTED},
    DocumentLifecycle.APPROVED: {DocumentLifecycle.ARCHIVED, DocumentLifecycle.EXPIRED},
    DocumentLifecycle.REJECTED: {DocumentLifecycle.DRAFT, DocumentLifecycle.ARCHIVED},
    DocumentLifecycle.ARCHIVED: {DocumentLifecycle.APPROVED, DocumentLifecycle.EXPIRED},
    DocumentLifecycle.EXPIRED: {DocumentLifecycle.ARCHIVED},
    DocumentLifecycle.QUARANTINED: {DocumentLifecycle.DRAFT},
}


def ensure_transition(current: str, target: DocumentLifecycle) -> None:
    try:
        state = DocumentLifecycle(current)
    except ValueError as exc:
        raise DocumentStateError("Document has an unsupported lifecycle state") from exc
    if target not in _ALLOWED.get(state, set()):
        raise DocumentStateError("The requested document state transition is not allowed", details={"current": state.value, "target": target.value})


def lifecycle_for_decision(decision: ReviewDecision) -> DocumentLifecycle:
    if decision == ReviewDecision.APPROVE:
        return DocumentLifecycle.APPROVED
    if decision == ReviewDecision.REJECT:
        return DocumentLifecycle.REJECTED
    return DocumentLifecycle.SUBMITTED
