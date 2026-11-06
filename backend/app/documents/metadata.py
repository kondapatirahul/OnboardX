import json
import re
from app.documents.constants import MAX_METADATA_KEYS, MAX_METADATA_VALUE_LENGTH, SENSITIVE_METADATA_KEYS
from app.documents.errors import DocumentValidationError

_KEY = re.compile(r"^[a-zA-Z][a-zA-Z0-9_.-]{0,63}$")


def sanitize_metadata(value: dict | None) -> dict:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise DocumentValidationError("Metadata must be an object")
    if len(value) > MAX_METADATA_KEYS:
        raise DocumentValidationError("Too many metadata fields")
    clean = {}
    for raw_key, raw_value in value.items():
        key = str(raw_key).strip()
        normalized = key.lower()
        if not _KEY.fullmatch(key):
            raise DocumentValidationError("Metadata contains an invalid key", details={"key": key[:80]})
        if normalized in SENSITIVE_METADATA_KEYS or any(part in normalized for part in ("password", "secret", "token")):
            raise DocumentValidationError("Sensitive values cannot be stored as document metadata", details={"key": key})
        if isinstance(raw_value, (dict, list)):
            encoded = json.dumps(raw_value, ensure_ascii=False, separators=(",", ":"))
        elif raw_value is None or isinstance(raw_value, (str, int, float, bool)):
            encoded = raw_value
        else:
            raise DocumentValidationError("Metadata values must be JSON-compatible")
        if isinstance(encoded, str) and len(encoded) > MAX_METADATA_VALUE_LENGTH:
            raise DocumentValidationError("Metadata value is too long", details={"key": key})
        clean[key] = encoded
    return clean


def encode_metadata(value: dict | None) -> str:
    return json.dumps(sanitize_metadata(value), ensure_ascii=False, separators=(",", ":"))


def decode_metadata(value: str | None) -> dict:
    if not value:
        return {}
    try:
        parsed = json.loads(value)
    except (TypeError, ValueError):
        return {}
    return parsed if isinstance(parsed, dict) else {}
