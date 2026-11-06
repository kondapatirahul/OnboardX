from datetime import datetime
from app.documents.enums import DocumentEventType, DocumentLifecycle, ReviewDecision
from app.documents.errors import DocumentForbidden, DocumentNotFound, DocumentStateError
from app.documents.transitions import ensure_transition, lifecycle_for_decision
from app.models.models import DocumentReview, DocumentStatus, Notification, NotificationType
from app.services.documents.activity import record_activity


class DocumentReviewService:
    def __init__(self, repository):
        self.repository = repository

    def review(self, *, user, document_id, decision, comments=None, ip_address=None):
        if user.role.value not in {"HR_ADMIN", "SUPER_ADMIN"}:
            raise DocumentForbidden("Only HR administrators can review documents")
        document = self.repository.document(user.organization_id, document_id)
        if not document:
            raise DocumentNotFound("Document was not found")
        if document.scan_status == "suspicious":
            raise DocumentStateError("A suspicious document cannot be approved")
        if document.lifecycle not in {DocumentLifecycle.SUBMITTED.value, DocumentLifecycle.IN_REVIEW.value}:
            raise DocumentStateError("Only submitted documents can be reviewed")
        target = lifecycle_for_decision(decision)
        ensure_transition(document.lifecycle, target)
        previous = document.lifecycle
        document.lifecycle = target.value
        document.status = DocumentStatus.APPROVED if decision == ReviewDecision.APPROVE else DocumentStatus.REJECTED if decision == ReviewDecision.REJECT else DocumentStatus.PENDING
        document.updated_by = user.id
        document.updated_at = datetime.utcnow()
        review = DocumentReview(
            document_id=document.id,
            reviewed_by=user.id,
            status=document.status,
            comments=comments,
            decision=decision.value,
            previous_status=previous,
            reviewed_at=datetime.utcnow(),
        )
        self.repository.db.add(review)
        employee_user_id = document.employee.user_id if document.employee else None
        if employee_user_id and decision in {ReviewDecision.APPROVE, ReviewDecision.REJECT}:
            notification_type = NotificationType.DOCUMENT_APPROVED if decision == ReviewDecision.APPROVE else NotificationType.DOCUMENT_REJECTED
            self.repository.db.add(Notification(
                user_id=employee_user_id,
                organization_id=user.organization_id,
                type=notification_type,
                title="Document review completed",
                message=f"Your document '{document.file_name}' was {decision.value}.",
                reference_id=document.id,
                reference_type="document",
            ))
        event = DocumentEventType.APPROVED if decision == ReviewDecision.APPROVE else DocumentEventType.REJECTED if decision == ReviewDecision.REJECT else DocumentEventType.CHANGES_REQUESTED
        record_activity(self.repository.db, document, user.id, event.value, f"Document {decision.value.replace('_', ' ')}", {"previous": previous, "target": target.value, "comments": comments}, ip_address)
        self.repository.commit()
        return document, review

    def start_review(self, *, user, document_id, ip_address=None):
        if user.role.value not in {"HR_ADMIN", "SUPER_ADMIN"}:
            raise DocumentForbidden("Only HR administrators can start reviews")
        document = self.repository.document(user.organization_id, document_id)
        if not document:
            raise DocumentNotFound("Document was not found")
        ensure_transition(document.lifecycle, DocumentLifecycle.IN_REVIEW)
        previous = document.lifecycle
        document.lifecycle = DocumentLifecycle.IN_REVIEW.value
        document.updated_by = user.id
        self.repository.db.add(DocumentReview(
            document_id=document.id, reviewed_by=user.id, status="pending",
            decision="start_review", previous_status=previous,
        ))
        record_activity(self.repository.db, document, user.id, DocumentEventType.REVIEW_STARTED.value, "Review started", {"previous": previous}, ip_address)
        self.repository.commit()
        return document

    def history(self, user, document_id):
        document = self.repository.document(user.organization_id, document_id)
        if not document:
            raise DocumentNotFound("Document was not found")
        return self.repository.reviews(user.organization_id, document_id)
