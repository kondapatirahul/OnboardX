import os
import tempfile
from pathlib import Path
from uuid import UUID
from app.documents.constants import DEFAULT_STORAGE_ROOT
from app.documents.errors import DocumentStorageError


class LocalDocumentStorage:
    """Filesystem storage that keeps client filenames outside physical paths."""

    def __init__(self, root: str | Path | None = None):
        configured = root or os.getenv("ONBOARDX_DOCUMENT_STORAGE") or DEFAULT_STORAGE_ROOT
        self.root = Path(configured).expanduser().resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def _target(self, organization_id: UUID, document_id: UUID, version: int, suffix: str) -> Path:
        if version < 1:
            raise DocumentStorageError("Invalid document version")
        suffix = suffix.lower()
        if len(suffix) > 12 or (suffix and not suffix.startswith(".")):
            raise DocumentStorageError("Invalid storage extension")
        target = self.root / str(organization_id) / str(document_id) / f"v{version}{suffix}"
        resolved = target.resolve()
        if self.root not in resolved.parents:
            raise DocumentStorageError("Storage path escaped configured root")
        return resolved

    def save(self, organization_id: UUID, document_id: UUID, version: int, suffix: str, content: bytes) -> str:
        target = self._target(organization_id, document_id, version, suffix)
        target.parent.mkdir(parents=True, exist_ok=True)
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(dir=target.parent, prefix=".upload-", delete=False) as stream:
                temporary = Path(stream.name)
                stream.write(content)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, target)
            return str(target)
        except OSError as exc:
            if temporary and temporary.exists():
                temporary.unlink(missing_ok=True)
            raise DocumentStorageError("Could not persist document content") from exc

    def read(self, stored_path: str) -> bytes:
        path = self._resolve_stored_path(stored_path)
        try:
            return path.read_bytes()
        except OSError as exc:
            raise DocumentStorageError("Could not read document content") from exc

    def open_stream(self, stored_path: str, chunk_size: int = 1024 * 1024):
        path = self._resolve_stored_path(stored_path)
        try:
            stream = path.open("rb")
        except OSError as exc:
            raise DocumentStorageError("Could not open document content") from exc
        try:
            while chunk := stream.read(chunk_size):
                yield chunk
        finally:
            stream.close()

    def delete(self, stored_path: str) -> None:
        path = self._resolve_stored_path(stored_path)
        try:
            path.unlink(missing_ok=True)
            self._remove_empty_parents(path.parent)
        except OSError as exc:
            raise DocumentStorageError("Could not delete stored document") from exc

    def exists(self, stored_path: str) -> bool:
        return self._resolve_stored_path(stored_path).is_file()

    def size(self, stored_path: str) -> int:
        path = self._resolve_stored_path(stored_path)
        try:
            return path.stat().st_size
        except OSError as exc:
            raise DocumentStorageError("Could not inspect stored document") from exc

    def _resolve_stored_path(self, stored_path: str) -> Path:
        path = Path(stored_path).expanduser().resolve()
        if self.root not in path.parents:
            raise DocumentStorageError("Stored path is outside configured storage root")
        return path

    def _remove_empty_parents(self, directory: Path) -> None:
        current = directory
        while current != self.root and self.root in current.parents:
            try:
                current.rmdir()
            except OSError:
                break
            current = current.parent
