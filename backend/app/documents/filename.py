import re
import unicodedata
from pathlib import PurePath
from app.documents.constants import MAX_FILENAME_LENGTH
from app.documents.errors import DocumentValidationError

_CONTROL = re.compile(r"[\x00-\x1f\x7f]")
_UNSAFE = re.compile(r"[^\w.() -]+", re.UNICODE)


def normalize_filename(value: str) -> str:
    if not value or not value.strip():
        raise DocumentValidationError("A filename is required")
    normalized = unicodedata.normalize("NFKC", value).strip()
    normalized = normalized.replace("\\", "/")
    normalized = PurePath(normalized).name
    normalized = _CONTROL.sub("", normalized)
    normalized = _UNSAFE.sub("_", normalized)
    normalized = normalized.strip(" .")
    if not normalized:
        raise DocumentValidationError("The filename is invalid")
    if len(normalized) > MAX_FILENAME_LENGTH:
        stem = PurePath(normalized).stem[: MAX_FILENAME_LENGTH - 16]
        normalized = f"{stem}{PurePath(normalized).suffix[:15]}"
    if normalized in {".", ".."}:
        raise DocumentValidationError("The filename is invalid")
    return normalized


def extension_of(filename: str) -> str:
    return PurePath(normalize_filename(filename)).suffix.lower()


def safe_download_name(filename: str) -> str:
    normalized = normalize_filename(filename)
    return normalized.replace('"', "'").replace(";", "_")
