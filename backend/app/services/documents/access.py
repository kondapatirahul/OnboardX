import hashlib
import secrets
from datetime import datetime, timedelta
from app.documents.enums import DocumentEventType
from app.documents.errors import DocumentConflict, DocumentForbidden, DocumentNotFound
from app.models.models import DocumentAccessGrant, DocumentShare
from app.services.documents.activity import record_activity


class DocumentAccessService:
    def __init__(self, repository):
        self.repository = repository

    def grant(self, *, user, document_id, target_user_id, permission="view", expires_at=None, ip_address=None):
        if user.role.value not in {"HR_ADMIN", "SUPER_ADMIN"}:
            raise DocumentForbidden("Only HR administrators can grant document access")
        document = self.repository.document(user.organization_id, document_id)
        target = self.repository.user(user.organization_id, target_user_id)
        if not document or not target:
            raise DocumentNotFound("Document or target user was not found")
        if permission not in {"view", "download", "manage"}:
            raise DocumentConflict("Unsupported access permission")
        existing = self.repository.grant(user.organization_id, document_id, target_user_id)
        if existing:
            existing.permission = permission
            existing.expires_at = expires_at
            existing.is_active = True
            existing.revoked_at = None
            grant = existing
        else:
            grant = self.repository.add_grant(DocumentAccessGrant(
                document_id=document.id, organization_id=user.organization_id,
                user_id=target_user_id, granted_by=user.id, permission=permission,
                expires_at=expires_at,
            ))
        record_activity(self.repository.db, document, user.id, DocumentEventType.SHARED.value,
                        "Document access granted", {"user_id": str(target_user_id), "permission": permission}, ip_address)
        self.repository.commit()
        return grant

    def revoke(self, *, user, document_id, grant_id, ip_address=None):
        if user.role.value not in {"HR_ADMIN", "SUPER_ADMIN"}:
            raise DocumentForbidden("Only HR administrators can revoke document access")
        document = self.repository.document(user.organization_id, document_id)
        if not document:
            raise DocumentNotFound("Document was not found")
        grant = self.repository.db.query(DocumentAccessGrant).filter(
            DocumentAccessGrant.id == grant_id,
            DocumentAccessGrant.document_id == document_id,
            DocumentAccessGrant.organization_id == user.organization_id,
        ).first()
        if not grant:
            raise DocumentNotFound("Access grant was not found")
        grant.is_active = False
        grant.revoked_at = datetime.utcnow()
        record_activity(self.repository.db, document, user.id, DocumentEventType.ACCESS_REVOKED.value,
                        "Document access revoked", {"user_id": str(grant.user_id)}, ip_address)
        self.repository.commit()
        return grant

    def list_grants(self, user, document_id):
        if user.role.value not in {"HR_ADMIN", "SUPER_ADMIN"}:
            raise DocumentForbidden("Only HR administrators can view access grants")
        document = self.repository.document(user.organization_id, document_id)
        if not document:
            raise DocumentNotFound("Document was not found")
        return self.repository.grants(user.organization_id, document_id)

    def create_share(self, *, user, document_id, expires_in_hours=72, max_downloads=None, ip_address=None):
        if user.role.value not in {"HR_ADMIN", "SUPER_ADMIN"}:
            raise DocumentForbidden("Only HR administrators can create share links")
        document = self.repository.document(user.organization_id, document_id)
        if not document:
            raise DocumentNotFound("Document was not found")
        raw_token = secrets.token_urlsafe(36)
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
        share = self.repository.add_share(DocumentShare(
            document_id=document.id,
            organization_id=user.organization_id,
            token_hash=token_hash,
            created_by=user.id,
            expires_at=datetime.utcnow() + timedelta(hours=expires_in_hours),
            max_downloads=max_downloads,
        ))
        record_activity(self.repository.db, document, user.id, DocumentEventType.SHARED.value,
                        "Secure share link created", {"expires_at": share.expires_at.isoformat()}, ip_address)
        self.repository.commit()
        return share, raw_token

    def revoke_share(self, *, user, document_id, share_id):
        if user.role.value not in {"HR_ADMIN", "SUPER_ADMIN"}:
            raise DocumentForbidden("Only HR administrators can revoke share links")
        document = self.repository.document(user.organization_id, document_id)
        if not document:
            raise DocumentNotFound("Document was not found")
        share = self.repository.db.query(DocumentShare).filter(
            DocumentShare.id == share_id,
            DocumentShare.document_id == document_id,
            DocumentShare.organization_id == user.organization_id,
        ).first()
        if not share:
            raise DocumentNotFound("Share link was not found")
        share.revoked_at = datetime.utcnow()
        self.repository.commit()
        return share

    def resolve_share(self, raw_token):
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
        share = self.repository.share_by_hash(token_hash)
        if not share or share.revoked_at or share.expires_at <= datetime.utcnow():
            raise DocumentNotFound("Share link is invalid or expired")
        if share.max_downloads is not None and share.download_count >= share.max_downloads:
            raise DocumentConflict("Share link download limit has been reached")
        document = self.repository.document(share.organization_id, share.document_id)
        if not document or document.lifecycle in {"quarantined", "deleted"}:
            raise DocumentNotFound("Shared document is unavailable")
        share.download_count += 1
        self.repository.commit()
        return document
