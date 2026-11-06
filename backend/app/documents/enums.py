from enum import Enum


class DocumentLifecycle(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    ARCHIVED = "archived"
    EXPIRED = "expired"
    QUARANTINED = "quarantined"


class DocumentVisibility(str, Enum):
    PRIVATE = "private"
    EMPLOYEE_AND_HR = "employee_and_hr"
    HR_ONLY = "hr_only"
    ORGANIZATION = "organization"


class ReviewDecision(str, Enum):
    APPROVE = "approve"
    REJECT = "reject"
    REQUEST_CHANGES = "request_changes"


class ScanStatus(str, Enum):
    NOT_SCANNED = "not_scanned"
    CLEAN = "clean"
    SUSPICIOUS = "suspicious"
    FAILED = "failed"


class RetentionAction(str, Enum):
    ARCHIVE = "archive"
    DELETE = "delete"
    REVIEW = "review"


class DocumentEventType(str, Enum):
    CREATED = "created"
    UPLOADED = "uploaded"
    VERSION_ADDED = "version_added"
    METADATA_UPDATED = "metadata_updated"
    SUBMITTED = "submitted"
    REVIEW_STARTED = "review_started"
    APPROVED = "approved"
    REJECTED = "rejected"
    CHANGES_REQUESTED = "changes_requested"
    DOWNLOADED = "downloaded"
    SHARED = "shared"
    ACCESS_REVOKED = "access_revoked"
    ARCHIVED = "archived"
    RESTORED = "restored"
    EXPIRED = "expired"
    DELETED = "deleted"
    RETENTION_APPLIED = "retention_applied"
