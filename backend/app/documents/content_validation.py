import hashlib
from app.documents.constants import ALLOWED_EXTENSIONS, ALLOWED_MIME_TYPES, MAGIC_SIGNATURES
from app.documents.errors import DocumentValidationError
from app.documents.filename import extension_of


def sha256_bytes(content: bytes) -> str:
    digest = hashlib.sha256()
    digest.update(content)
    return digest.hexdigest()


def detect_mime(content: bytes, declared: str | None = None) -> str:
    for signature, mime in MAGIC_SIGNATURES.items():
        if content.startswith(signature):
            if signature == b"RIFF" and content[8:12] == b"WEBP":
                return "image/webp"
            return mime
    if declared and declared.lower().startswith("text/"):
        try:
            content[:8192].decode("utf-8")
            return declared.lower()
        except UnicodeDecodeError:
            pass
    if declared and declared in ALLOWED_MIME_TYPES:
        return declared
    return "application/octet-stream"


def validate_upload(filename: str, content: bytes, declared_mime: str | None, max_bytes: int) -> tuple[str, str]:
    extension = extension_of(filename)
    if extension not in ALLOWED_EXTENSIONS:
        raise DocumentValidationError("File extension is not allowed", details={"extension": extension})
    if not content:
        raise DocumentValidationError("Empty files cannot be uploaded")
    if len(content) > max_bytes:
        raise DocumentValidationError("File exceeds the upload size limit", details={"max_bytes": max_bytes})
    detected = detect_mime(content, declared_mime)
    if detected not in ALLOWED_MIME_TYPES:
        raise DocumentValidationError("File content type is not allowed", details={"mime_type": detected})
    expected_by_extension = {
        ".pdf": "application/pdf", ".png": "image/png", ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg", ".webp": "image/webp", ".txt": "text/plain",
        ".csv": "text/csv",
    }
    expected = expected_by_extension.get(extension)
    if expected and detected not in {expected, "application/octet-stream"}:
        raise DocumentValidationError("File extension does not match file content")
    return detected, sha256_bytes(content)
