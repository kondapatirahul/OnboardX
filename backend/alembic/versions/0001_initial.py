"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2025-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '0001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # organizations
    op.create_table(
        'organizations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('slug', sa.String(100), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slug'),
    )
    op.create_index('ix_organizations_slug', 'organizations', ['slug'])

    # departments
    op.create_table(
        'departments',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )

    # users
    userrole_enum = postgresql.ENUM('SUPER_ADMIN', 'HR_ADMIN', 'MANAGER', 'EMPLOYEE', name='userrole')
    userrole_enum.create(op.get_bind())
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(255), nullable=False),
        sa.Column('role', sa.Enum('SUPER_ADMIN', 'HR_ADMIN', 'MANAGER', 'EMPLOYEE', name='userrole'), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
    )
    op.create_index('ix_users_email', 'users', ['email'])

    # employees
    employeestatus_enum = postgresql.ENUM('active', 'inactive', 'onboarding', 'offboarding', name='employeestatus')
    employeestatus_enum.create(op.get_bind())
    op.create_table(
        'employees',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('employee_id', sa.String(50), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('department_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('designation', sa.String(255), nullable=True),
        sa.Column('joining_date', sa.DateTime(), nullable=True),
        sa.Column('manager_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('status', sa.Enum('active', 'inactive', 'onboarding', 'offboarding', name='employeestatus'), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['department_id'], ['departments.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['manager_id'], ['employees.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('employee_id'),
    )
    op.create_index('ix_employees_employee_id', 'employees', ['employee_id'])

    # onboarding_templates
    op.create_table(
        'onboarding_templates',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )

    # onboarding_stages
    op.create_table(
        'onboarding_stages',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('template_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('order_index', sa.Integer(), nullable=False),
        sa.Column('duration_days', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['template_id'], ['onboarding_templates.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )

    # onboarding_instances
    onboardingstatus_enum = postgresql.ENUM('not_started', 'in_progress', 'completed', 'on_hold', name='onboardingstatus')
    onboardingstatus_enum.create(op.get_bind())
    op.create_table(
        'onboarding_instances',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('employee_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('template_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('status', sa.Enum('not_started', 'in_progress', 'completed', 'on_hold', name='onboardingstatus'), nullable=True),
        sa.Column('progress_percentage', sa.Float(), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['template_id'], ['onboarding_templates.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )

    # onboarding_tasks
    taskstatus_enum = postgresql.ENUM('pending', 'in_progress', 'completed', 'overdue', 'cancelled', name='taskstatus')
    taskstatus_enum.create(op.get_bind())
    taskpriority_enum = postgresql.ENUM('low', 'medium', 'high', 'urgent', name='taskpriority')
    taskpriority_enum.create(op.get_bind())
    op.create_table(
        'onboarding_tasks',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('instance_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('stage_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('assigned_to', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('assigned_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('status', sa.Enum('pending', 'in_progress', 'completed', 'overdue', 'cancelled', name='taskstatus'), nullable=True),
        sa.Column('priority', sa.Enum('low', 'medium', 'high', 'urgent', name='taskpriority'), nullable=True),
        sa.Column('due_date', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['assigned_by'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['assigned_to'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['instance_id'], ['onboarding_instances.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['stage_id'], ['onboarding_stages.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )

    # documents
    documentstatus_enum = postgresql.ENUM('pending', 'approved', 'rejected', name='documentstatus')
    documentstatus_enum.create(op.get_bind())
    op.create_table(
        'documents',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('employee_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('document_type', sa.String(100), nullable=False),
        sa.Column('file_name', sa.String(255), nullable=False),
        sa.Column('file_path', sa.String(500), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=True),
        sa.Column('mime_type', sa.String(100), nullable=True),
        sa.Column('status', sa.Enum('pending', 'approved', 'rejected', name='documentstatus'), nullable=True),
        sa.Column('uploaded_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )

    # document_reviews
    op.create_table(
        'document_reviews',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('document_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('reviewed_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('status', sa.Enum('pending', 'approved', 'rejected', name='documentstatus'), nullable=False),
        sa.Column('comments', sa.Text(), nullable=True),
        sa.Column('reviewed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['reviewed_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )

    # training_courses
    op.create_table(
        'training_courses',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('content_url', sa.String(500), nullable=True),
        sa.Column('duration_minutes', sa.Integer(), nullable=True),
        sa.Column('is_mandatory', sa.Boolean(), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )

    # training_assignments
    op.create_table(
        'training_assignments',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('course_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('employee_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('assigned_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('status', sa.Enum('pending', 'in_progress', 'completed', 'overdue', 'cancelled', name='taskstatus'), nullable=True),
        sa.Column('progress_percentage', sa.Float(), nullable=True),
        sa.Column('due_date', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('assigned_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['assigned_by'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['course_id'], ['training_courses.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )

    # notifications
    notificationtype_enum = postgresql.ENUM(
        'task_assigned', 'task_overdue', 'document_approved', 'document_rejected',
        'onboarding_started', 'onboarding_completed', 'joining_reminder', 'general',
        name='notificationtype'
    )
    notificationtype_enum.create(op.get_bind())
    op.create_table(
        'notifications',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('type', sa.Enum(
            'task_assigned', 'task_overdue', 'document_approved', 'document_rejected',
            'onboarding_started', 'onboarding_completed', 'joining_reminder', 'general',
            name='notificationtype'
        ), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('is_read', sa.Boolean(), nullable=True),
        sa.Column('reference_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('reference_type', sa.String(50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )

    # calendar_events
    op.create_table(
        'calendar_events',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('event_type', sa.String(50), nullable=False),
        sa.Column('start_date', sa.DateTime(), nullable=False),
        sa.Column('end_date', sa.DateTime(), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('employee_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )

    # audit_logs
    op.create_table(
        'audit_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('action', sa.String(100), nullable=False),
        sa.Column('resource_type', sa.String(100), nullable=False),
        sa.Column('resource_id', sa.String(255), nullable=True),
        sa.Column('details', sa.Text(), nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade() -> None:
    op.drop_table('audit_logs')
    op.drop_table('calendar_events')
    op.drop_table('notifications')
    op.drop_table('training_assignments')
    op.drop_table('training_courses')
    op.drop_table('document_reviews')
    op.drop_table('documents')
    op.drop_table('onboarding_tasks')
    op.drop_table('onboarding_instances')
    op.drop_table('onboarding_stages')
    op.drop_table('onboarding_templates')
    op.drop_table('employees')
    op.drop_table('users')
    op.drop_table('departments')
    op.drop_table('organizations')

    for enum_name in ['notificationtype', 'documentstatus', 'taskpriority', 'taskstatus',
                      'onboardingstatus', 'employeestatus', 'userrole']:
        op.execute(f'DROP TYPE IF EXISTS {enum_name}')
