from datetime import datetime
from app.documents.enums import DocumentEventType, DocumentLifecycle
from app.documents.errors import DocumentConflict, DocumentForbidden, DocumentNotFound, DocumentStateError
from app.documents.metadata import decode_metadata
from app.documents.permissions import can_download_document, can_view_document
from app.documents.pagination import page_window, page_count
from app.models.models import Document, DocumentAccessGrant
from app.services.documents.activity import record_activity


class DocumentManagerService:
    def __init__(self, repository, storage):
        self.repository = repository
        self.storage = storage

    def get(self, *, user, document_id):
        document = self.repository.document(user.organization_id, document_id)
        if not document:
            raise DocumentNotFound("Document was not found")
        grant = self.repository.grant(user.organization_id, document_id, user.id)
        if not can_view_document(user, document, document.employee, grant):
            raise DocumentForbidden("You do not have access to this document")
        return document

    def list(self, *, user, employee_id=None, category=None, lifecycle=None, status=None,
             visibility=None, search=None, tag=None, expires_before=None,
             created_after=None, created_before=None, page=1, page_size=25, sort="newest"):
        window = page_window(page, page_size)
        if user.role.value == "EMPLOYEE":
            employee = getattr(user, "employee", None)
            if not employee:
                return {"items": [], "pagination": {"page": page, "page_size": page_size, "total": 0, "pages": 0}}
            employee_id = employee.id
        items, total = self.repository.list_documents(
            user.organization_id, employee_id=employee_id, category=category,
            lifecycle=lifecycle, status=status, visibility=visibility,
            search=search, tag=tag, expires_before=expires_before,
            created_after=created_after, created_before=created_before,
            offset=window.offset, limit=window.limit, sort=sort,
        )
        if user.role.value == "EMPLOYEE":
            items = [item for item in items if can_view_document(user, item, item.employee)]
            total = len(items)
        return {"items": items, "pagination": {"page": page, "page_size": page_size, "total": total, "pages": page_count(total, page_size)}}

    def download(self, *, user, document_id, version_number=None, ip_address=None):
        document = self.repository.document(user.organization_id, document_id)
        if not document:
            raise DocumentNotFound("Document was not found")
        grant = self.repository.grant(user.organization_id, document_id, user.id)
        if not can_download_document(user, document, document.employee, grant):
            raise DocumentForbidden("You do not have permission to download this document")
        path = document.file_path
        if version_number is not None:
            version = self.repository.version(user.organization_id, document_id, version_number)
            if not version:
                raise DocumentNotFound("Document version was not found")
            path = version.file_path
        if not self.storage.exists(path):
            raise DocumentNotFound("Stored document content is unavailable")
        record_activity(self.repository.db, document, user.id, DocumentEventType.DOWNLOADED.value,
                        "Document downloaded", {"version": version_number or document.current_version}, ip_address)
        self.repository.commit()
        return document, path

    def archive(self, *, user, document_id, ip_address=None):
        if user.role.value not in {"HR_ADMIN", "SUPER_ADMIN"}:
            raise DocumentForbidden("Only HR administrators can archive documents")
        document = self.repository.document(user.organization_id, document_id)
        if not document:
            raise DocumentNotFound("Document was not found")
        if document.lifecycle == DocumentLifecycle.ARCHIVED.value:
            return document
        if document.lifecycle in {DocumentLifecycle.QUARANTINED.value, DocumentLifecycle.EXPIRED.value}:
            raise DocumentStateError("This document cannot be archived from its current state")
        document.lifecycle = DocumentLifecycle.ARCHIVED.value
        document.archived_at = datetime.utcnow()
        document.updated_by = user.id
        record_activity(self.repository.db, document, user.id, DocumentEventType.ARCHIVED.value, "Document archived", {}, ip_address)
        self.repository.commit()
        return document

    def restore(self, *, user, document_id, ip_address=None):
        if user.role.value not in {"HR_ADMIN", "SUPER_ADMIN"}:
            raise DocumentForbidden("Only HR administrators can restore documents")
        document = self.repository.document(user.organization_id, document_id, include_deleted=True)
        if not document or document.deleted_at:
            raise DocumentNotFound("Document was not found")
        if document.lifecycle != DocumentLifecycle.ARCHIVED.value:
            raise DocumentStateError("Only archived documents can be restored")
        document.lifecycle = DocumentLifecycle.APPROVED.value if document.status == "approved" else DocumentLifecycle.SUBMITTED.value
        document.archived_at = None
        document.updated_by = user.id
        record_activity(self.repository.db, document, user.id, DocumentEventType.RESTORED.value, "Document restored", {}, ip_address)
        self.repository.commit()
        return document

    def soft_delete(self, *, user, document_id, ip_address=None):
        if user.role.value not in {"HR_ADMIN", "SUPER_ADMIN"}:
            raise DocumentForbidden("Only HR administrators can delete documents")
        document = self.repository.document(user.organization_id, document_id)
        if not document:
            raise DocumentNotFound("Document was not found")
        if document.lifecycle == DocumentLifecycle.IN_REVIEW.value:
            raise DocumentConflict("A document under review cannot be deleted")
        document.deleted_at = datetime.utcnow()
        document.lifecycle = "deleted"
        document.updated_by = user.id
        record_activity(self.repository.db, document, user.id, DocumentEventType.DELETED.value, "Document soft deleted", {}, ip_address)
        self.repository.commit()
        return document

    def activity(self, user, document_id, page=1, page_size=50):
        document = self.get(user=user, document_id=document_id)
        window = page_window(page, page_size)
        items = self.repository.activity(user.organization_id, document.id, offset=window.offset, limit=window.limit)
        return items

    def summary(self, user, employee_id=None):
        query = self.repository.db.query(Document).filter(
            Document.organization_id == user.organization_id,
            Document.deleted_at.is_(None),
        )
        if user.role.value == "EMPLOYEE":
            employee = getattr(user, "employee", None)
            if not employee:
                return {"total": 0, "pending": 0, "approved": 0, "rejected": 0, "expiring_soon": 0, "storage_bytes": 0}
            employee_id = employee.id
        if employee_id:
            query = query.filter(Document.employee_id == employee_id)
        rows = query.all()
        now = datetime.utcnow()
        soon = [row for row in rows if row.expires_at and now <= row.expires_at <= now.replace(hour=23, minute=59, second=59) + __import__("datetime").timedelta(days=30)]
        return {
            "total": len(rows),
            "pending": sum(row.lifecycle in {"submitted", "in_review"} for row in rows),
            "approved": sum(row.lifecycle == "approved" for row in rows),
            "rejected": sum(row.lifecycle == "rejected" for row in rows),
            "archived": sum(row.lifecycle == "archived" for row in rows),
            "expiring_soon": len(soon),
            "storage_bytes": sum(row.file_size or 0 for row in rows),
        }
