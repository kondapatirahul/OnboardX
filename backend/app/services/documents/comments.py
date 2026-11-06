from datetime import datetime
from app.documents.errors import DocumentForbidden, DocumentNotFound, DocumentValidationError
from app.models.models import DocumentComment


class DocumentCommentService:
    def __init__(self, repository):
        self.repository = repository

    def add(self, *, user, document_id, body, is_internal=False, parent_id=None):
        document = self.repository.document(user.organization_id, document_id)
        if not document:
            raise DocumentNotFound("Document was not found")
        if is_internal and user.role.value not in {"HR_ADMIN", "SUPER_ADMIN"}:
            raise DocumentForbidden("Only HR administrators can add internal comments")
        if user.role.value == "EMPLOYEE" and document.employee.user_id != user.id:
            raise DocumentForbidden("You cannot comment on this document")
        if parent_id:
            parent = self.repository.db.query(DocumentComment).filter(
                DocumentComment.id == parent_id,
                DocumentComment.document_id == document_id,
                DocumentComment.organization_id == user.organization_id,
                DocumentComment.deleted_at.is_(None),
            ).first()
            if not parent:
                raise DocumentValidationError("Parent comment was not found")
        comment = self.repository.add_comment(DocumentComment(
            document_id=document.id, organization_id=user.organization_id,
            author_id=user.id, body=body.strip(), is_internal=is_internal,
            parent_id=parent_id,
        ))
        self.repository.commit()
        return comment

    def list(self, user, document_id):
        document = self.repository.document(user.organization_id, document_id)
        if not document:
            raise DocumentNotFound("Document was not found")
        internal = user.role.value in {"HR_ADMIN", "SUPER_ADMIN"}
        return self.repository.comments(user.organization_id, document_id, include_internal=internal)

    def edit(self, *, user, document_id, comment_id, body):
        comment = self.repository.db.query(DocumentComment).filter(
            DocumentComment.id == comment_id,
            DocumentComment.document_id == document_id,
            DocumentComment.organization_id == user.organization_id,
            DocumentComment.deleted_at.is_(None),
        ).first()
        if not comment:
            raise DocumentNotFound("Comment was not found")
        if comment.author_id != user.id and user.role.value not in {"HR_ADMIN", "SUPER_ADMIN"}:
            raise DocumentForbidden("You cannot edit this comment")
        comment.body = body.strip()
        comment.edited_at = datetime.utcnow()
        self.repository.commit()
        return comment

    def delete(self, *, user, document_id, comment_id):
        comment = self.repository.db.query(DocumentComment).filter(
            DocumentComment.id == comment_id,
            DocumentComment.document_id == document_id,
            DocumentComment.organization_id == user.organization_id,
            DocumentComment.deleted_at.is_(None),
        ).first()
        if not comment:
            raise DocumentNotFound("Comment was not found")
        if comment.author_id != user.id and user.role.value not in {"HR_ADMIN", "SUPER_ADMIN"}:
            raise DocumentForbidden("You cannot delete this comment")
        comment.deleted_at = datetime.utcnow()
        comment.body = "[deleted]"
        self.repository.commit()
        return True
