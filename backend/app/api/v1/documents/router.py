import json
from datetime import datetime
from pathlib import Path
from uuid import UUID
from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, Request, UploadFile, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.core.deps import get_current_user, require_hr_or_above
from app.db.session import get_db
from app.documents.constants import DEFAULT_MAX_UPLOAD_BYTES
from app.documents.enums import ReviewDecision
from app.documents.errors import DocumentError
from app.documents.filename import safe_download_name
from app.models.models import User
from app.repositories.documents.repository import DocumentRepository
from app.schemas.documents import (
    AccessGrantInput, AccessGrantOut, ActivityOut, CommentInput, CommentOut,
    DocumentOut, DocumentPage, DocumentUpdate, ReviewInput, ReviewOut,
    RetentionPolicyInput, RetentionPolicyOut, RetentionPolicyUpdate, ShareInput, TagInput, TagOut,
    VersionOut,
)
from app.services.documents.access import DocumentAccessService
from app.services.documents.catalog import DocumentCatalogService
from app.services.documents.comments import DocumentCommentService
from app.services.documents.manager import DocumentManagerService
from app.services.documents.retention import DocumentRetentionService
from app.services.documents.review import DocumentReviewService
from app.services.documents.upload import DocumentUploadService
from app.services.documents.versioning import DocumentVersionService
from app.storage.local import LocalDocumentStorage

router = APIRouter()
storage = LocalDocumentStorage()


def _services(db: Session):
    repository = DocumentRepository(db)
    return {
        "repository": repository,
        "manager": DocumentManagerService(repository, storage),
        "upload": DocumentUploadService(repository, storage),
        "review": DocumentReviewService(repository),
        "versions": DocumentVersionService(repository, storage, DEFAULT_MAX_UPLOAD_BYTES),
        "access": DocumentAccessService(repository),
        "catalog": DocumentCatalogService(repository),
        "comments": DocumentCommentService(repository),
        "retention": DocumentRetentionService(repository),
    }


def _run(callable_):
    try:
        return callable_()
    except DocumentError as exc:
        raise exc.as_http_exception() from exc


def _ip(request: Request):
    return request.client.host if request.client else None


@router.get("/categories")
def document_categories(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    from sqlalchemy import func
    from app.models.models import Document
    rows = db.query(Document.category, func.count(Document.id)).filter(
        Document.organization_id == user.organization_id,
        Document.deleted_at.is_(None),
        Document.category.is_not(None),
    ).group_by(Document.category).order_by(Document.category.asc()).all()
    return [{"category": category, "count": count} for category, count in rows]


@router.get("/shared/{token}/download")
def download_shared_document(token: str, db: Session = Depends(get_db)):
    services = _services(db)
    document = _run(lambda: services["access"].resolve_share(token))
    if not storage.exists(document.file_path):
        raise HTTPException(status_code=404, detail="Shared document content is unavailable")
    filename = safe_download_name(document.file_name)
    return StreamingResponse(storage.open_stream(document.file_path), media_type=document.mime_type or "application/octet-stream",
                             headers={"Content-Disposition": f'attachment; filename="{filename}"', "X-Content-Type-Options": "nosniff"})


@router.get("/summary")
def document_summary(
    employee_id: UUID | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    services = _services(db)
    return _run(lambda: services["manager"].summary(user, employee_id))


@router.post("/upload", response_model=DocumentOut, status_code=status.HTTP_201_CREATED)
async def upload_document(
    request: Request,
    employee_id: UUID = Form(...),
    category: str = Form(..., min_length=2, max_length=80),
    title: str | None = Form(default=None, max_length=180),
    description: str | None = Form(default=None, max_length=4000),
    visibility: str = Form(default="employee_and_hr"),
    expires_at: datetime | None = Form(default=None),
    metadata: str = Form(default="{}"),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    content = await file.read(DEFAULT_MAX_UPLOAD_BYTES + 1)
    if len(content) > DEFAULT_MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="File exceeds upload size limit")
    try:
        metadata_value = json.loads(metadata or "{}")
    except ValueError as exc:
        raise HTTPException(status_code=422, detail="Metadata must be valid JSON") from exc
    services = _services(db)
    return _run(lambda: services["upload"].upload(
        user=user, employee_id=employee_id, filename=file.filename or "upload.bin",
        content=content, content_type=file.content_type, category=category,
        title=title, description=description, visibility=visibility,
        expires_at=expires_at, metadata=metadata_value, ip_address=_ip(request),
    ))


@router.get("", response_model=DocumentPage)
def list_documents(
    employee_id: UUID | None = None,
    category: str | None = None,
    lifecycle: str | None = None,
    status_filter: str | None = Query(default=None, alias="status"),
    visibility: str | None = None,
    search: str | None = Query(default=None, max_length=160),
    tag: str | None = Query(default=None, max_length=48),
    expires_before: datetime | None = None,
    created_after: datetime | None = None,
    created_before: datetime | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=1, le=100),
    sort: str = Query(default="newest", pattern="^(newest|oldest|name|expiry)$"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    services = _services(db)
    return _run(lambda: services["manager"].list(
        user=user, employee_id=employee_id, category=category, lifecycle=lifecycle,
        status=status_filter, visibility=visibility, search=search, tag=tag,
        expires_before=expires_before, created_after=created_after,
        created_before=created_before, page=page, page_size=page_size, sort=sort,
    ))


@router.get("/{document_id:uuid}", response_model=DocumentOut)
def get_document(document_id: UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    services = _services(db)
    return _run(lambda: services["manager"].get(user=user, document_id=document_id))


@router.patch("/{document_id:uuid}", response_model=DocumentOut)
def update_document(document_id: UUID, payload: DocumentUpdate, request: Request,
                    db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    services = _services(db)
    values = payload.model_dump(exclude_unset=True)
    return _run(lambda: services["catalog"].update_metadata(user=user, document_id=document_id, payload=values, ip_address=_ip(request)))


@router.get("/{document_id:uuid}/download")
def download_document(document_id: UUID, request: Request, version: int | None = Query(default=None, ge=1),
                      db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    services = _services(db)
    document, stored_path = _run(lambda: services["manager"].download(user=user, document_id=document_id, version_number=version, ip_address=_ip(request)))
    filename = safe_download_name(document.file_name)
    return StreamingResponse(storage.open_stream(stored_path), media_type=document.mime_type or "application/octet-stream",
                             headers={"Content-Disposition": f'attachment; filename="{filename}"', "X-Content-Type-Options": "nosniff"})


@router.post("/{document_id:uuid}/versions", response_model=VersionOut, status_code=201)
async def add_version(document_id: UUID, request: Request, file: UploadFile = File(...),
                      change_note: str | None = Form(default=None, max_length=1000),
                      db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    content = await file.read(DEFAULT_MAX_UPLOAD_BYTES + 1)
    if len(content) > DEFAULT_MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="File exceeds upload size limit")
    services = _services(db)
    return _run(lambda: services["versions"].add_version(user=user, document_id=document_id,
        filename=file.filename or "upload.bin", content=content, content_type=file.content_type,
        change_note=change_note, ip_address=_ip(request)))


@router.get("/{document_id:uuid}/versions", response_model=list[VersionOut])
def list_versions(document_id: UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    services = _services(db)
    return _run(lambda: services["versions"].list_versions(user, document_id))


@router.post("/{document_id:uuid}/versions/{version_number}/restore", response_model=VersionOut)
def restore_version(document_id: UUID, version_number: int, request: Request,
                    db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    services = _services(db)
    return _run(lambda: services["versions"].restore_version(user=user, document_id=document_id,
        version_number=version_number, ip_address=_ip(request)))


@router.post("/{document_id:uuid}/review/start", response_model=DocumentOut)
def start_review(document_id: UUID, request: Request, db: Session = Depends(get_db), user: User = Depends(require_hr_or_above)):
    services = _services(db)
    return _run(lambda: services["review"].start_review(user=user, document_id=document_id, ip_address=_ip(request)))


@router.post("/{document_id:uuid}/review", response_model=ReviewOut)
def review_document(document_id: UUID, payload: ReviewInput, request: Request,
                    db: Session = Depends(get_db), user: User = Depends(require_hr_or_above)):
    services = _services(db)
    _, review = _run(lambda: services["review"].review(user=user, document_id=document_id,
        decision=payload.decision, comments=payload.comments, ip_address=_ip(request)))
    return review


@router.get("/{document_id:uuid}/reviews", response_model=list[ReviewOut])
def review_history(document_id: UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    services = _services(db)
    return _run(lambda: services["review"].history(user, document_id))


@router.get("/reviews/queue")
def review_queue(page: int = Query(default=1, ge=1), page_size: int = Query(default=25, ge=1, le=100),
                employee_id: UUID | None = None, db: Session = Depends(get_db), user: User = Depends(require_hr_or_above)):
    services = _services(db)
    offset = (page - 1) * page_size
    items, total = services["repository"].pending_review_queue(user.organization_id, offset=offset, limit=page_size, employee_id=employee_id)
    return {"items": items, "page": page, "page_size": page_size, "total": total}


@router.get("/{document_id:uuid}/metadata")
def get_metadata(document_id: UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    services = _services(db)
    return _run(lambda: services["catalog"].metadata(user, document_id))


@router.get("/{document_id:uuid}/tags", response_model=list[TagOut])
def list_tags(document_id: UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    services = _services(db)
    return _run(lambda: services["catalog"].tags(user, document_id))


@router.post("/{document_id:uuid}/tags", response_model=TagOut, status_code=201)
def add_tag(document_id: UUID, payload: TagInput, request: Request, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    services = _services(db)
    return _run(lambda: services["catalog"].add_tag(user=user, document_id=document_id, name=payload.name, ip_address=_ip(request)))


@router.delete("/{document_id:uuid}/tags/{tag_id}", status_code=204)
def remove_tag(document_id: UUID, tag_id: UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    services = _services(db)
    _run(lambda: services["catalog"].remove_tag(user=user, document_id=document_id, tag_id=tag_id))


@router.get("/{document_id:uuid}/activity", response_model=list[ActivityOut])
def document_activity(document_id: UUID, page: int = Query(default=1, ge=1), page_size: int = Query(default=50, ge=1, le=100),
                      db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    services = _services(db)
    return _run(lambda: services["manager"].activity(user, document_id, page, page_size))


@router.get("/{document_id:uuid}/comments", response_model=list[CommentOut])
def list_comments(document_id: UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    services = _services(db)
    return _run(lambda: services["comments"].list(user, document_id))


@router.post("/{document_id:uuid}/comments", response_model=CommentOut, status_code=201)
def add_comment(document_id: UUID, payload: CommentInput, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    services = _services(db)
    return _run(lambda: services["comments"].add(user=user, document_id=document_id,
        body=payload.body, is_internal=payload.is_internal, parent_id=payload.parent_id))


@router.patch("/{document_id:uuid}/comments/{comment_id}", response_model=CommentOut)
def edit_comment(document_id: UUID, comment_id: UUID, payload: CommentInput,
                 db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    services = _services(db)
    return _run(lambda: services["comments"].edit(user=user, document_id=document_id, comment_id=comment_id, body=payload.body))


@router.delete("/{document_id:uuid}/comments/{comment_id}", status_code=204)
def delete_comment(document_id: UUID, comment_id: UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    services = _services(db)
    _run(lambda: services["comments"].delete(user=user, document_id=document_id, comment_id=comment_id))


@router.post("/{document_id:uuid}/access", response_model=AccessGrantOut, status_code=201)
def grant_access(document_id: UUID, payload: AccessGrantInput, request: Request,
                 db: Session = Depends(get_db), user: User = Depends(require_hr_or_above)):
    services = _services(db)
    return _run(lambda: services["access"].grant(user=user, document_id=document_id,
        target_user_id=payload.user_id, permission=payload.permission, expires_at=payload.expires_at, ip_address=_ip(request)))


@router.get("/{document_id:uuid}/access", response_model=list[AccessGrantOut])
def list_access(document_id: UUID, db: Session = Depends(get_db), user: User = Depends(require_hr_or_above)):
    services = _services(db)
    return _run(lambda: services["access"].list_grants(user, document_id))


@router.delete("/{document_id:uuid}/access/{grant_id}", response_model=AccessGrantOut)
def revoke_access(document_id: UUID, grant_id: UUID, request: Request,
                  db: Session = Depends(get_db), user: User = Depends(require_hr_or_above)):
    services = _services(db)
    return _run(lambda: services["access"].revoke(user=user, document_id=document_id, grant_id=grant_id, ip_address=_ip(request)))


@router.post("/{document_id:uuid}/shares")
def create_share(document_id: UUID, payload: ShareInput, request: Request,
                 db: Session = Depends(get_db), user: User = Depends(require_hr_or_above)):
    services = _services(db)
    share, token = _run(lambda: services["access"].create_share(user=user, document_id=document_id,
        expires_in_hours=payload.expires_in_hours, max_downloads=payload.max_downloads, ip_address=_ip(request)))
    return {"id": str(share.id), "token": token, "expires_at": share.expires_at, "max_downloads": share.max_downloads}


@router.delete("/{document_id:uuid}/shares/{share_id}")
def revoke_share(document_id: UUID, share_id: UUID, db: Session = Depends(get_db), user: User = Depends(require_hr_or_above)):
    services = _services(db)
    share = _run(lambda: services["access"].revoke_share(user=user, document_id=document_id, share_id=share_id))
    return {"id": str(share.id), "revoked": bool(share.revoked_at)}


@router.post("/{document_id:uuid}/archive", response_model=DocumentOut)
def archive_document(document_id: UUID, request: Request, db: Session = Depends(get_db), user: User = Depends(require_hr_or_above)):
    services = _services(db)
    return _run(lambda: services["manager"].archive(user=user, document_id=document_id, ip_address=_ip(request)))


@router.post("/{document_id:uuid}/restore", response_model=DocumentOut)
def restore_document(document_id: UUID, request: Request, db: Session = Depends(get_db), user: User = Depends(require_hr_or_above)):
    services = _services(db)
    return _run(lambda: services["manager"].restore(user=user, document_id=document_id, ip_address=_ip(request)))


@router.delete("/{document_id:uuid}", response_model=DocumentOut)
def delete_document(document_id: UUID, request: Request, db: Session = Depends(get_db), user: User = Depends(require_hr_or_above)):
    services = _services(db)
    return _run(lambda: services["manager"].soft_delete(user=user, document_id=document_id, ip_address=_ip(request)))


@router.get("/retention/policies", response_model=list[RetentionPolicyOut])
def list_retention_policies(include_inactive: bool = False, db: Session = Depends(get_db), user: User = Depends(require_hr_or_above)):
    services = _services(db)
    return _run(lambda: services["retention"].list_policies(user, include_inactive))


@router.post("/retention/policies", response_model=RetentionPolicyOut, status_code=201)
def create_retention_policy(payload: RetentionPolicyInput, db: Session = Depends(get_db), user: User = Depends(require_hr_or_above)):
    services = _services(db)
    return _run(lambda: services["retention"].create_policy(user=user, name=payload.name,
        category=payload.category, retention_days=payload.retention_days,
        action=payload.action, is_active=payload.is_active))


@router.patch("/retention/policies/{policy_id}", response_model=RetentionPolicyOut)
def update_retention_policy(policy_id: UUID, payload: RetentionPolicyUpdate,
                            db: Session = Depends(get_db), user: User = Depends(require_hr_or_above)):
    services = _services(db)
    return _run(lambda: services["retention"].update_policy(user=user, policy_id=policy_id,
        values=payload.model_dump(exclude_unset=True)))


@router.get("/retention/policies/{policy_id}/preview")
def preview_retention(policy_id: UUID, db: Session = Depends(get_db), user: User = Depends(require_hr_or_above)):
    services = _services(db)
    return _run(lambda: services["retention"].preview(user, policy_id))


@router.post("/retention/policies/{policy_id}/execute")
def execute_retention(policy_id: UUID, dry_run: bool = Query(default=True),
                      db: Session = Depends(get_db), user: User = Depends(require_hr_or_above)):
    services = _services(db)
    return _run(lambda: services["retention"].execute(user=user, policy_id=policy_id, dry_run=dry_run))
