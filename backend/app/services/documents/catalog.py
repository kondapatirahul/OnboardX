from datetime import datetime
from app.documents.constants import MAX_TAGS_PER_DOCUMENT
from app.documents.enums import DocumentEventType
from app.documents.errors import DocumentConflict, DocumentForbidden, DocumentNotFound, DocumentValidationError
from app.documents.metadata import decode_metadata, encode_metadata
from app.models.models import DocumentTag
from app.services.documents.activity import record_activity


class DocumentCatalogService:
    def __init__(self, repository):
        self.repository = repository

    def update_metadata(self, *, user, document_id, payload, ip_address=None):
        document = self.repository.document(user.organization_id, document_id)
        if not document:
            raise DocumentNotFound("Document was not found")
        if user.role.value == "EMPLOYEE" and document.employee.user_id != user.id:
            raise DocumentForbidden("You cannot edit this document")
        changed = {}
        for key in ("title", "description", "category", "visibility", "expires_at"):
            value = payload.get(key)
            if key in payload:
                setattr(document, key, value.value if hasattr(value, "value") else value)
                changed[key] = value.isoformat() if hasattr(value, "isoformat") else value
        if "metadata" in payload:
            document.metadata_json = encode_metadata(payload["metadata"])
            changed["metadata_keys"] = sorted(payload["metadata"].keys())
        document.updated_by = user.id
        document.updated_at = datetime.utcnow()
        record_activity(self.repository.db, document, user.id, DocumentEventType.METADATA_UPDATED.value,
                        "Document details updated", changed, ip_address)
        self.repository.commit()
        return document

    def metadata(self, user, document_id):
        document = self.repository.document(user.organization_id, document_id)
        if not document:
            raise DocumentNotFound("Document was not found")
        return decode_metadata(document.metadata_json)

    def add_tag(self, *, user, document_id, name, ip_address=None):
        document = self.repository.document(user.organization_id, document_id)
        if not document:
            raise DocumentNotFound("Document was not found")
        if user.role.value == "EMPLOYEE" and document.employee.user_id != user.id:
            raise DocumentForbidden("You cannot tag this document")
        normalized = name.strip().lower()
        if not normalized or len(normalized) > 48:
            raise DocumentValidationError("Tag name is invalid")
        existing = self.repository.tag(user.organization_id, document_id, normalized)
        if existing:
            return existing
        if len(self.repository.tags(user.organization_id, document_id)) >= MAX_TAGS_PER_DOCUMENT:
            raise DocumentConflict("Document tag limit has been reached")
        tag = self.repository.add_tag(DocumentTag(
            document_id=document.id, organization_id=user.organization_id,
            name=name.strip(), normalized_name=normalized, created_by=user.id,
        ))
        record_activity(self.repository.db, document, user.id, "tag_added", "Document tag added", {"tag": normalized}, ip_address)
        self.repository.commit()
        return tag

    def remove_tag(self, *, user, document_id, tag_id):
        document = self.repository.document(user.organization_id, document_id)
        if not document:
            raise DocumentNotFound("Document was not found")
        if user.role.value == "EMPLOYEE" and document.employee.user_id != user.id:
            raise DocumentForbidden("You cannot modify this document")
        tag = self.repository.db.query(DocumentTag).filter(
            DocumentTag.id == tag_id,
            DocumentTag.document_id == document_id,
            DocumentTag.organization_id == user.organization_id,
        ).first()
        if not tag:
            raise DocumentNotFound("Tag was not found")
        self.repository.db.delete(tag)
        record_activity(self.repository.db, document, user.id, "tag_removed", "Document tag removed", {"tag": tag.normalized_name})
        self.repository.commit()
        return True

    def tags(self, user, document_id):
        document = self.repository.document(user.organization_id, document_id)
        if not document:
            raise DocumentNotFound("Document was not found")
        return self.repository.tags(user.organization_id, document_id)
