from datetime import datetime
from uuid import UUID
from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Session, joinedload
from app.models.models import (
    Document, DocumentVersion, DocumentReview, DocumentAccessGrant,
    DocumentTag, DocumentActivity, DocumentComment, DocumentRetentionPolicy,
    DocumentShare, Employee, User,
)


class DocumentRepository:
    def __init__(self, db: Session):
        self.db = db

    def employee(self, organization_id: UUID, employee_id: UUID):
        return self.db.query(Employee).filter(
            Employee.id == employee_id,
            Employee.organization_id == organization_id,
        ).first()

    def user(self, organization_id: UUID, user_id: UUID):
        return self.db.query(User).filter(
            User.id == user_id,
            User.organization_id == organization_id,
            User.is_active.is_(True),
        ).first()

    def document(self, organization_id: UUID, document_id: UUID, *, include_deleted=False):
        query = self.db.query(Document).options(
            joinedload(Document.employee).joinedload(Employee.user),
            joinedload(Document.reviews),
        ).filter(
            Document.id == document_id,
            Document.organization_id == organization_id,
        )
        if not include_deleted:
            query = query.filter(Document.deleted_at.is_(None))
        return query.first()

    def list_documents(self, organization_id: UUID, *, employee_id=None, category=None,
                       lifecycle=None, status=None, visibility=None, search=None,
                       tag=None, expires_before=None, created_after=None,
                       created_before=None, offset=0, limit=25, sort="newest"):
        query = self.db.query(Document).filter(
            Document.organization_id == organization_id,
            Document.deleted_at.is_(None),
        )
        if employee_id:
            query = query.filter(Document.employee_id == employee_id)
        if category:
            query = query.filter(Document.category == category)
        if lifecycle:
            query = query.filter(Document.lifecycle == lifecycle)
        if status:
            query = query.filter(Document.status == status)
        if visibility:
            query = query.filter(Document.visibility == visibility)
        if search:
            needle = f"%{search.strip()}%"
            query = query.filter(or_(Document.file_name.ilike(needle), Document.title.ilike(needle), Document.description.ilike(needle), Document.document_type.ilike(needle)))
        if tag:
            query = query.join(DocumentTag, DocumentTag.document_id == Document.id).filter(DocumentTag.normalized_name == tag.lower())
        if expires_before:
            query = query.filter(Document.expires_at.is_not(None), Document.expires_at <= expires_before)
        if created_after:
            query = query.filter(Document.uploaded_at >= created_after)
        if created_before:
            query = query.filter(Document.uploaded_at <= created_before)
        if sort == "oldest":
            query = query.order_by(Document.uploaded_at.asc(), Document.id.asc())
        elif sort == "name":
            query = query.order_by(Document.file_name.asc(), Document.id.asc())
        elif sort == "expiry":
            query = query.order_by(Document.expires_at.asc().nullslast(), Document.id.asc())
        else:
            query = query.order_by(Document.uploaded_at.desc(), Document.id.desc())
        total = query.with_entities(func.count(func.distinct(Document.id))).scalar() or 0
        items = query.distinct(Document.id).offset(offset).limit(limit).all()
        return items, total

    def add_document(self, document: Document):
        self.db.add(document)
        self.db.flush()
        return document

    def versions(self, organization_id: UUID, document_id: UUID):
        return self.db.query(DocumentVersion).filter(
            DocumentVersion.organization_id == organization_id,
            DocumentVersion.document_id == document_id,
        ).order_by(DocumentVersion.version_number.desc()).all()

    def version(self, organization_id: UUID, document_id: UUID, version_number: int):
        return self.db.query(DocumentVersion).filter(
            DocumentVersion.organization_id == organization_id,
            DocumentVersion.document_id == document_id,
            DocumentVersion.version_number == version_number,
        ).first()

    def add_version(self, version: DocumentVersion):
        self.db.add(version)
        self.db.flush()
        return version

    def reviews(self, organization_id: UUID, document_id: UUID):
        return self.db.query(DocumentReview).join(Document).filter(
            Document.organization_id == organization_id,
            DocumentReview.document_id == document_id,
        ).order_by(DocumentReview.reviewed_at.desc()).all()

    def pending_review_queue(self, organization_id: UUID, *, offset=0, limit=25, employee_id=None):
        query = self.db.query(Document).options(joinedload(Document.employee).joinedload(Employee.user)).filter(
            Document.organization_id == organization_id,
            Document.deleted_at.is_(None),
            Document.lifecycle.in_(["submitted", "in_review"]),
        )
        if employee_id:
            query = query.filter(Document.employee_id == employee_id)
        total = query.count()
        return query.order_by(Document.uploaded_at.asc()).offset(offset).limit(limit).all(), total

    def grant(self, organization_id: UUID, document_id: UUID, user_id: UUID):
        return self.db.query(DocumentAccessGrant).filter(
            DocumentAccessGrant.organization_id == organization_id,
            DocumentAccessGrant.document_id == document_id,
            DocumentAccessGrant.user_id == user_id,
            DocumentAccessGrant.is_active.is_(True),
            or_(DocumentAccessGrant.expires_at.is_(None), DocumentAccessGrant.expires_at > datetime.utcnow()),
        ).first()

    def grants(self, organization_id: UUID, document_id: UUID):
        return self.db.query(DocumentAccessGrant).filter(
            DocumentAccessGrant.organization_id == organization_id,
            DocumentAccessGrant.document_id == document_id,
        ).order_by(DocumentAccessGrant.created_at.desc()).all()

    def add_grant(self, grant: DocumentAccessGrant):
        self.db.add(grant)
        self.db.flush()
        return grant

    def tags(self, organization_id: UUID, document_id: UUID):
        return self.db.query(DocumentTag).filter(
            DocumentTag.organization_id == organization_id,
            DocumentTag.document_id == document_id,
        ).order_by(DocumentTag.normalized_name.asc()).all()

    def tag(self, organization_id: UUID, document_id: UUID, normalized_name: str):
        return self.db.query(DocumentTag).filter(
            DocumentTag.organization_id == organization_id,
            DocumentTag.document_id == document_id,
            DocumentTag.normalized_name == normalized_name,
        ).first()

    def add_tag(self, tag: DocumentTag):
        self.db.add(tag)
        self.db.flush()
        return tag

    def activity(self, organization_id: UUID, document_id: UUID, *, offset=0, limit=50):
        return self.db.query(DocumentActivity).filter(
            DocumentActivity.organization_id == organization_id,
            DocumentActivity.document_id == document_id,
        ).order_by(DocumentActivity.created_at.desc()).offset(offset).limit(limit).all()

    def add_activity(self, activity: DocumentActivity):
        self.db.add(activity)
        self.db.flush()
        return activity

    def comments(self, organization_id: UUID, document_id: UUID, *, include_internal=False):
        query = self.db.query(DocumentComment).filter(
            DocumentComment.organization_id == organization_id,
            DocumentComment.document_id == document_id,
            DocumentComment.deleted_at.is_(None),
        )
        if not include_internal:
            query = query.filter(DocumentComment.is_internal.is_(False))
        return query.order_by(DocumentComment.created_at.asc()).all()

    def add_comment(self, comment: DocumentComment):
        self.db.add(comment)
        self.db.flush()
        return comment

    def retention_policies(self, organization_id: UUID, active_only=True):
        query = self.db.query(DocumentRetentionPolicy).filter(DocumentRetentionPolicy.organization_id == organization_id)
        if active_only:
            query = query.filter(DocumentRetentionPolicy.is_active.is_(True))
        return query.order_by(DocumentRetentionPolicy.name.asc()).all()

    def add_retention_policy(self, policy: DocumentRetentionPolicy):
        self.db.add(policy)
        self.db.flush()
        return policy

    def share_by_hash(self, token_hash: str):
        return self.db.query(DocumentShare).filter(DocumentShare.token_hash == token_hash).first()

    def add_share(self, share: DocumentShare):
        self.db.add(share)
        self.db.flush()
        return share

    def commit(self):
        self.db.commit()

    def rollback(self):
        self.db.rollback()
