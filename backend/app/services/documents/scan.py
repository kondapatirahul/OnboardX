from dataclasses import dataclass
from typing import Protocol
from app.documents.enums import DocumentEventType, ScanStatus
from app.documents.errors import DocumentNotFound
from app.services.documents.activity import record_activity


@dataclass(frozen=True)
class ScanResult:
    status: ScanStatus
    engine: str
    message: str | None = None


class ContentScanner(Protocol):
    def scan(self, content: bytes, filename: str) -> ScanResult: ...


class DisabledScanner:
    """Explicit no-op scanner; deployments should inject a real scanner."""
    def scan(self, content: bytes, filename: str) -> ScanResult:
        return ScanResult(ScanStatus.NOT_SCANNED, "disabled", "No malware scanner is configured")


class DocumentScanService:
    def __init__(self, repository, storage, scanner: ContentScanner):
        self.repository = repository
        self.storage = storage
        self.scanner = scanner

    def scan_document(self, *, organization_id, document_id, actor_id=None):
        document = self.repository.document(organization_id, document_id)
        if not document:
            raise DocumentNotFound("Document was not found")
        content = self.storage.read(document.file_path)
        result = self.scanner.scan(content, document.file_name)
        document.scan_status = result.status.value
        if result.status == ScanStatus.SUSPICIOUS:
            document.lifecycle = "quarantined"
        record_activity(self.repository.db, document, actor_id, "scan_completed",
                        "Document content scan completed", {"status": result.status.value, "engine": result.engine, "message": result.message})
        self.repository.commit()
        return result
