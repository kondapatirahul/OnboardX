from datetime import datetime, timedelta
from app.documents.enums import DocumentEventType, DocumentLifecycle, RetentionAction
from app.documents.errors import DocumentForbidden, DocumentNotFound, DocumentValidationError
from app.models.models import Document, DocumentRetentionPolicy, DocumentRetentionExecution
from app.services.documents.activity import record_activity


class DocumentRetentionService:
    def __init__(self, repository):
        self.repository = repository

    def create_policy(self, *, user, name, category, retention_days, action, is_active=True):
        if user.role.value not in {"HR_ADMIN", "SUPER_ADMIN"}:
            raise DocumentForbidden("Only HR administrators can manage retention policies")
        if retention_days < 1 or retention_days > 36500:
            raise DocumentValidationError("Retention period is outside the allowed range")
        policy = self.repository.add_retention_policy(DocumentRetentionPolicy(
            organization_id=user.organization_id, name=name.strip(), category=category,
            retention_days=retention_days, action=action, is_active=is_active,
            created_by=user.id,
        ))
        self.repository.commit()
        return policy

    def list_policies(self, user, include_inactive=False):
        if user.role.value not in {"HR_ADMIN", "SUPER_ADMIN"}:
            raise DocumentForbidden("Only HR administrators can view retention policies")
        return self.repository.retention_policies(user.organization_id, active_only=not include_inactive)

    def update_policy(self, *, user, policy_id, values):
        if user.role.value not in {"HR_ADMIN", "SUPER_ADMIN"}:
            raise DocumentForbidden("Only HR administrators can manage retention policies")
        policy = self.repository.db.query(DocumentRetentionPolicy).filter(
            DocumentRetentionPolicy.id == policy_id,
            DocumentRetentionPolicy.organization_id == user.organization_id,
        ).first()
        if not policy:
            raise DocumentNotFound("Retention policy was not found")
        for key in ("name", "category", "retention_days", "action", "is_active"):
            if key in values:
                setattr(policy, key, values[key])
        policy.updated_at = datetime.utcnow()
        self.repository.commit()
        return policy

    def preview(self, user, policy_id):
        if user.role.value not in {"HR_ADMIN", "SUPER_ADMIN"}:
            raise DocumentForbidden("Only HR administrators can preview retention")
        policy = self.repository.db.query(DocumentRetentionPolicy).filter(
            DocumentRetentionPolicy.id == policy_id,
            DocumentRetentionPolicy.organization_id == user.organization_id,
            DocumentRetentionPolicy.is_active.is_(True),
        ).first()
        if not policy:
            raise DocumentNotFound("Retention policy was not found")
        cutoff = datetime.utcnow() - timedelta(days=policy.retention_days)
        query = self.repository.db.query(Document).filter(
            Document.organization_id == user.organization_id,
            Document.deleted_at.is_(None),
            Document.uploaded_at <= cutoff,
        )
        if policy.category:
            query = query.filter(Document.category == policy.category)
        candidates = query.order_by(Document.uploaded_at.asc()).limit(1000).all()
        return {"policy_id": str(policy.id), "cutoff": cutoff, "count": len(candidates), "document_ids": [str(item.id) for item in candidates]}

    def execute(self, *, user, policy_id, document_ids=None, dry_run=True):
        if user.role.value not in {"HR_ADMIN", "SUPER_ADMIN"}:
            raise DocumentForbidden("Only HR administrators can execute retention")
        policy = self.repository.db.query(DocumentRetentionPolicy).filter(
            DocumentRetentionPolicy.id == policy_id,
            DocumentRetentionPolicy.organization_id == user.organization_id,
            DocumentRetentionPolicy.is_active.is_(True),
        ).first()
        if not policy:
            raise DocumentNotFound("Retention policy was not found")
        cutoff = datetime.utcnow() - timedelta(days=policy.retention_days)
        query = self.repository.db.query(Document).filter(
            Document.organization_id == user.organization_id,
            Document.deleted_at.is_(None),
            Document.uploaded_at <= cutoff,
        )
        if policy.category:
            query = query.filter(Document.category == policy.category)
        if document_ids:
            query = query.filter(Document.id.in_(document_ids))
        candidates = query.limit(1000).all()
        results = []
        for document in candidates:
            if dry_run:
                results.append({"document_id": str(document.id), "action": policy.action, "result": "preview"})
                continue
            if policy.action == RetentionAction.ARCHIVE.value:
                document.lifecycle = DocumentLifecycle.ARCHIVED.value
                document.archived_at = datetime.utcnow()
            elif policy.action == RetentionAction.DELETE.value:
                document.deleted_at = datetime.utcnow()
                document.lifecycle = "deleted"
            elif policy.action == RetentionAction.REVIEW.value:
                document.lifecycle = DocumentLifecycle.EXPIRED.value
            execution = DocumentRetentionExecution(
                policy_id=policy.id, document_id=document.id,
                organization_id=user.organization_id, action=policy.action,
                result="applied", executed_by=user.id,
            )
            self.repository.db.add(execution)
            record_activity(self.repository.db, document, user.id, DocumentEventType.RETENTION_APPLIED.value,
                            "Retention policy applied", {"policy": str(policy.id), "action": policy.action})
            results.append({"document_id": str(document.id), "action": policy.action, "result": "applied"})
        if not dry_run:
            self.repository.commit()
        return {"dry_run": dry_run, "processed": len(results), "results": results}
