from fastapi import HTTPException, status


class DocumentError(Exception):
    """Base class for document-domain failures."""

    status_code = status.HTTP_400_BAD_REQUEST
    code = "document_error"

    def __init__(self, message: str, *, details: dict | None = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def as_http_exception(self) -> HTTPException:
        return HTTPException(
            status_code=self.status_code,
            detail={"code": self.code, "message": self.message, "details": self.details},
        )


class DocumentNotFound(DocumentError):
    status_code = status.HTTP_404_NOT_FOUND
    code = "document_not_found"


class DocumentForbidden(DocumentError):
    status_code = status.HTTP_403_FORBIDDEN
    code = "document_forbidden"


class DocumentConflict(DocumentError):
    status_code = status.HTTP_409_CONFLICT
    code = "document_conflict"


class DocumentValidationError(DocumentError):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    code = "document_validation_error"


class DocumentStorageError(DocumentError):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    code = "document_storage_error"


class DocumentStateError(DocumentError):
    status_code = status.HTTP_409_CONFLICT
    code = "invalid_document_state"
