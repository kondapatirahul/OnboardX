from datetime import datetime
from uuid import uuid4
from app.documents.constants import DEFAULT_MAX_UPLOAD_BYTES, ABSOLUTE_MAX_UPLOAD_BYTES
from app.documents.content_validation import validate_upload
from app.documents.enums import DocumentEventType, DocumentLifecycle, DocumentVisibility, ScanStatus
from app.documents.errors import DocumentNotFound, DocumentValidationError
from app.documents.filename import normalize_filename, extension_of
from app.documents.metadata import encode_metadata
from app.models.models import Document, DocumentVersion, Employee
from app.services.documents.activity import record_activity


class DocumentUploadService:
    def __init__(self, repository, storage, max_upload_bytes=DEFAULT_MAX_UPLOAD_BYTES):
        self.repository = repository
        self.storage = storage
        self.max_upload_bytes = min(max_upload_bytes, ABSOLUTE_MAX_UPLOAD_BYTES)

    def upload(self, *, user, employee_id, filename, content, content_type, category,
               title=None, description=None, visibility=DocumentVisibility.EMPLOYEE_AND_HR.value,
               expires_at=None, metadata=None, ip_address=None):
        employee = self.repository.employee(user.organization_id, employee_id)
        if not employee:
            raise DocumentNotFound("Employee was not found in this organization")
        if user.role.value == "EMPLOYEE" and employee.user_id != user.id:
            from app.documents.errors import DocumentForbidden
            raise DocumentForbidden("Employees can only upload their own documents")
        clean_name = normalize_filename(filename)
        detected_mime, checksum = validate_upload(clean_name, content, content_type, self.max_upload_bytes)
        document_id = uuid4()
        stored_path = self.storage.save(user.organization_id, document_id, 1, extension_of(clean_name), content)
        document = Document(
            id=document_id,
            employee_id=employee.id,
            organization_id=user.organization_id,
            document_type=category,
            file_name=clean_name,
            file_path=stored_path,
            file_size=len(content),
            mime_type=detected_mime,
            title=(title or clean_name)[:180],
            description=description,
            category=category,
            lifecycle=DocumentLifecycle.SUBMITTED.value,
            visibility=visibility,
            checksum_sha256=checksum,
            scan_status=ScanStatus.NOT_SCANNED.value,
            current_version=1,
            expires_at=expires_at,
            created_by=user.id,
            updated_by=user.id,
            metadata_json=encode_metadata(metadata),
            uploaded_at=datetime.utcnow(),
        )
        try:
            self.repository.add_document(document)
            self.repository.add_version(DocumentVersion(
                document_id=document.id,
                organization_id=user.organization_id,
                version_number=1,
                file_name=clean_name,
                file_path=stored_path,
                file_size=len(content),
                mime_type=detected_mime,
                checksum_sha256=checksum,
                uploaded_by=user.id,
            ))
            record_activity(self.repository.db, document, user.id, DocumentEventType.UPLOADED.value,
                            "Document uploaded", {"filename": clean_name, "size": len(content), "checksum": checksum}, ip_address)
            self.repository.commit()
        except Exception:
            self.repository.rollback()
            self.storage.delete(stored_path)
            raise
        return document
