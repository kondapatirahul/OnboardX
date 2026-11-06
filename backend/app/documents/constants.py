from pathlib import Path

DEFAULT_MAX_UPLOAD_BYTES = 25 * 1024 * 1024
ABSOLUTE_MAX_UPLOAD_BYTES = 100 * 1024 * 1024
CHUNK_SIZE = 1024 * 1024
MAX_FILENAME_LENGTH = 240
MAX_TITLE_LENGTH = 180
MAX_DESCRIPTION_LENGTH = 4000
MAX_TAGS_PER_DOCUMENT = 30
MAX_TAG_LENGTH = 48
MAX_METADATA_KEYS = 40
MAX_METADATA_VALUE_LENGTH = 1000
DEFAULT_PAGE_SIZE = 25
MAX_PAGE_SIZE = 100
DEFAULT_DOWNLOAD_URL_TTL_SECONDS = 300
DEFAULT_SHARE_TTL_HOURS = 72
ALLOWED_EXTENSIONS = {
    ".pdf", ".png", ".jpg", ".jpeg", ".webp", ".txt", ".csv",
    ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
}
ALLOWED_MIME_TYPES = {
    "application/pdf", "image/png", "image/jpeg", "image/webp",
    "text/plain", "text/csv", "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.ms-powerpoint",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "application/octet-stream",
}
MAGIC_SIGNATURES = {
    b"%PDF-": "application/pdf",
    b"\x89PNG\r\n\x1a\n": "image/png",
    b"\xff\xd8\xff": "image/jpeg",
    b"RIFF": "image/webp",
}
SENSITIVE_METADATA_KEYS = {
    "password", "secret", "token", "access_token", "refresh_token",
    "authorization", "cookie", "private_key", "api_key",
}
STORAGE_ROOT_ENV = "ONBOARDX_DOCUMENT_STORAGE"
DEFAULT_STORAGE_ROOT = Path("var") / "onboardx" / "documents"
