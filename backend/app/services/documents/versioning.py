from datetime import datetime
from app.documents.content_validation import validate_upload
from app.documents.enums import DocumentEventType, DocumentLifecycle
from app.documents.errors import DocumentForbidden, DocumentNotFound, DocumentStateError
from app.documents.filename import normalize_filename, extension_of
from app.models.models import DocumentVersion, DocumentStatus
from app.services.documents.activity import record_activity


class DocumentVersionService:
    def __init__(self, repository, storage, max_upload_bytes):
        self.repository = repository
        self.storage = storage
        self.max_upload_bytes = max_upload_bytes

    def add_version(self, *, user, document_id, filename, content, content_type, change_note=None, ip_address=None):
        document = self.repository.document(user.organization_id, document_id)
        if not document:
            raise DocumentNotFound("Document was not found")
        if user.role.value == "EMPLOYEE" and document.employee.user_id != user.id:
            raise DocumentForbidden("You cannot update this document")
        if document.lifecycle in {DocumentLifecycle.ARCHIVED.value, DocumentLifecycle.EXPIRED.value, DocumentLifecycle.QUARANTINED.value}:
            raise DocumentStateError("A new version cannot be added in the current state")
        clean_name = normalize_filename(filename)
        mime, checksum = validate_upload(clean_name, content, content_type, self.max_upload_bytes)
        next_version = document.current_version + 1
        stored_path = self.storage.save(user.organization_id, document.id, next_version, extension_of(clean_name), content)
        try:
            version = DocumentVersion(
                document_id=document.id,
                organization_id=user.organization_id,
                version_number=next_version,
                file_name=clean_name,
                file_path=stored_path,
                file_size=len(content),
                mime_type=mime,
                checksum_sha256=checksum,
                change_note=change_note,
                uploaded_by=user.id,
            )
            self.repository.add_version(version)
            document.file_name = clean_name
            document.file_path = stored_path
            document.file_size = len(content)
            document.mime_type = mime
            document.checksum_sha256 = checksum
            document.current_version = next_version
            document.lifecycle = DocumentLifecycle.SUBMITTED.value
            document.status = DocumentStatus.PENDING
            document.scan_status = "not_scanned"
            document.updated_by = user.id
            document.updated_at = datetime.utcnow()
            record_activity(self.repository.db, document, user.id, DocumentEventType.VERSION_ADDED.value,
                            f"Version {next_version} uploaded", {"version": next_version, "change_note": change_note}, ip_address)
            self.repository.commit()
        except Exception:
            self.repository.rollback()
            self.storage.delete(stored_path)
            raise
        return version

    def list_versions(self, user, document_id):
        document = self.repository.document(user.organization_id, document_id)
        if not document:
            raise DocumentNotFound("Document was not found")
        return self.repository.versions(user.organization_id, document_id)

    def restore_version(self, *, user, document_id, version_number, ip_address=None):
        document = self.repository.document(user.organization_id, document_id)
        if not document:
            raise DocumentNotFound("Document was not found")
        if user.role.value not in {"HR_ADMIN", "SUPER_ADMIN"}:
            raise DocumentForbidden("Only HR administrators can restore a version")
        version = self.repository.version(user.organization_id, document_id, version_number)
        if not version:
            raise DocumentNotFound("Document version was not found")
        content = self.storage.read(version.file_path)
        return self.add_version(
            user=user, document_id=document_id, filename=version.file_name,
            content=content, content_type=version.mime_type,
            change_note=f"Restored from version {version_number}", ip_address=ip_address,
        )
