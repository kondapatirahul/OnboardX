import enum
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Enum, ForeignKey, Text, Integer, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.session import Base


# ─── Enums ────────────────────────────────────────────────────────────────────

class UserRole(str, enum.Enum):
    SUPER_ADMIN = "SUPER_ADMIN"
    HR_ADMIN = "HR_ADMIN"
    MANAGER = "MANAGER"
    EMPLOYEE = "EMPLOYEE"


class EmployeeStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ONBOARDING = "onboarding"
    OFFBOARDING = "offboarding"


class OnboardingStatus(str, enum.Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ON_HOLD = "on_hold"


class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class TaskPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class DocumentStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class NotificationType(str, enum.Enum):
    TASK_ASSIGNED = "task_assigned"
    TASK_OVERDUE = "task_overdue"
    DOCUMENT_APPROVED = "document_approved"
    DOCUMENT_REJECTED = "document_rejected"
    ONBOARDING_STARTED = "onboarding_started"
    ONBOARDING_COMPLETED = "onboarding_completed"
    JOINING_REMINDER = "joining_reminder"
    GENERAL = "general"


# ─── Core Org Models ──────────────────────────────────────────────────────────

class Organization(Base):
    __tablename__ = "organizations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    users = relationship("User", back_populates="organization")
    departments = relationship("Department", back_populates="organization")
    onboarding_templates = relationship("OnboardingTemplate", back_populates="organization")


class Department(Base):
    __tablename__ = "departments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    organization = relationship("Organization", back_populates="departments")
    employees = relationship("Employee", back_populates="department")


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.EMPLOYEE)
    is_active = Column(Boolean, default=True)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    organization = relationship("Organization", back_populates="users")
    employee = relationship("Employee", back_populates="user", uselist=False)
    notifications = relationship("Notification", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")


class Employee(Base):
    __tablename__ = "employees"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    employee_id = Column(String(50), unique=True, nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    department_id = Column(UUID(as_uuid=True), ForeignKey("departments.id", ondelete="SET NULL"), nullable=True)
    designation = Column(String(255), nullable=True)
    joining_date = Column(DateTime, nullable=True)
    manager_id = Column(UUID(as_uuid=True), ForeignKey("employees.id", ondelete="SET NULL"), nullable=True)
    status = Column(Enum(EmployeeStatus), default=EmployeeStatus.ONBOARDING)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="employee")
    department = relationship("Department", back_populates="employees")
    manager = relationship("Employee", remote_side=[id], foreign_keys=[manager_id])
    onboarding_instances = relationship("OnboardingInstance", back_populates="employee")
    documents = relationship("Document", back_populates="employee")
    training_assignments = relationship("TrainingAssignment", back_populates="employee")


# ─── Onboarding Models ────────────────────────────────────────────────────────

class OnboardingTemplate(Base):
    __tablename__ = "onboarding_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    is_active = Column(Boolean, default=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    organization = relationship("Organization", back_populates="onboarding_templates")
    stages = relationship("OnboardingStage", back_populates="template", cascade="all, delete-orphan", order_by="OnboardingStage.order_index")
    instances = relationship("OnboardingInstance", back_populates="template")


class OnboardingStage(Base):
    __tablename__ = "onboarding_stages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    template_id = Column(UUID(as_uuid=True), ForeignKey("onboarding_templates.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    order_index = Column(Integer, nullable=False, default=0)
    duration_days = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    template = relationship("OnboardingTemplate", back_populates="stages")
    tasks = relationship("OnboardingTask", back_populates="stage", cascade="all, delete-orphan")


class OnboardingInstance(Base):
    __tablename__ = "onboarding_instances"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    template_id = Column(UUID(as_uuid=True), ForeignKey("onboarding_templates.id", ondelete="SET NULL"), nullable=True)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    status = Column(Enum(OnboardingStatus), default=OnboardingStatus.NOT_STARTED)
    progress_percentage = Column(Float, default=0.0)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    employee = relationship("Employee", back_populates="onboarding_instances")
    template = relationship("OnboardingTemplate", back_populates="instances")
    tasks = relationship("OnboardingTask", back_populates="instance")


class OnboardingTask(Base):
    __tablename__ = "onboarding_tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    instance_id = Column(UUID(as_uuid=True), ForeignKey("onboarding_instances.id", ondelete="CASCADE"), nullable=True)
    stage_id = Column(UUID(as_uuid=True), ForeignKey("onboarding_stages.id", ondelete="SET NULL"), nullable=True)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    assigned_to = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    assigned_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING)
    priority = Column(Enum(TaskPriority), default=TaskPriority.MEDIUM)
    due_date = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    instance = relationship("OnboardingInstance", back_populates="tasks")
    stage = relationship("OnboardingStage", back_populates="tasks")


# ─── Document Models ──────────────────────────────────────────────────────────

class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    document_type = Column(String(100), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=True)
    mime_type = Column(String(100), nullable=True)
    status = Column(Enum(DocumentStatus), default=DocumentStatus.PENDING)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    employee = relationship("Employee", back_populates="documents")
    reviews = relationship("DocumentReview", back_populates="document", cascade="all, delete-orphan")


class DocumentReview(Base):
    __tablename__ = "document_reviews"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    reviewed_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    status = Column(Enum(DocumentStatus), nullable=False)
    comments = Column(Text, nullable=True)
    reviewed_at = Column(DateTime, default=datetime.utcnow)

    document = relationship("Document", back_populates="reviews")


# ─── Training Models ──────────────────────────────────────────────────────────

class TrainingCourse(Base):
    __tablename__ = "training_courses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    content_url = Column(String(500), nullable=True)
    duration_minutes = Column(Integer, nullable=True)
    is_mandatory = Column(Boolean, default=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    assignments = relationship("TrainingAssignment", back_populates="course")


class TrainingAssignment(Base):
    __tablename__ = "training_assignments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    course_id = Column(UUID(as_uuid=True), ForeignKey("training_courses.id", ondelete="CASCADE"), nullable=False)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    assigned_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING)
    progress_percentage = Column(Float, default=0.0)
    due_date = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    assigned_at = Column(DateTime, default=datetime.utcnow)

    course = relationship("TrainingCourse", back_populates="assignments")
    employee = relationship("Employee", back_populates="training_assignments")


# ─── Notification Model ───────────────────────────────────────────────────────

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    type = Column(Enum(NotificationType), nullable=False, default=NotificationType.GENERAL)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    reference_id = Column(UUID(as_uuid=True), nullable=True)
    reference_type = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="notifications")


# ─── Calendar Model ───────────────────────────────────────────────────────────

class CalendarEvent(Base):
    __tablename__ = "calendar_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    event_type = Column(String(50), nullable=False, default="general")
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id", ondelete="CASCADE"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


# ─── Audit Log Model ──────────────────────────────────────────────────────────

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action = Column(String(100), nullable=False)
    resource_type = Column(String(100), nullable=False)
    resource_id = Column(String(255), nullable=True)
    details = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="audit_logs")
