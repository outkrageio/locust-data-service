"""Initial migration

Revision ID: 9cf07ff9990c
Revises:
Create Date: 2025-12-06 09:19:13.223197

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB


# revision identifiers, used by Alembic.
revision: str = '9cf07ff9990c'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create test_runs table
    op.create_table(
        'test_runs',
        sa.Column('id', UUID(as_uuid=True), nullable=False),
        sa.Column('project', sa.String(length=255), nullable=False),
        sa.Column('test_name', sa.String(length=255), nullable=False),
        sa.Column('start_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('end_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('user_count', sa.Integer(), nullable=False),
        sa.Column('spawn_rate', sa.Float(), nullable=False),
        sa.Column('host', sa.String(length=512), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('test_metadata', JSONB, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_test_runs_project_name', 'test_runs', ['project', 'test_name'])
    op.create_index('idx_test_runs_start_time', 'test_runs', ['start_time'])
    op.create_index('idx_test_runs_status', 'test_runs', ['status'])
    op.create_index(op.f('ix_test_runs_project'), 'test_runs', ['project'])
    op.create_index(op.f('ix_test_runs_test_name'), 'test_runs', ['test_name'])

    # Create request_logs table
    op.create_table(
        'request_logs',
        sa.Column('id', UUID(as_uuid=True), nullable=False),
        sa.Column('test_run_id', UUID(as_uuid=True), nullable=False),
        sa.Column('request_type', sa.String(length=10), nullable=False),
        sa.Column('name', sa.String(length=512), nullable=False),
        sa.Column('url', sa.String(length=2048), nullable=False),
        sa.Column('response_time', sa.Float(), nullable=False),
        sa.Column('response_length', sa.Integer(), nullable=False),
        sa.Column('success', sa.Boolean(), nullable=False),
        sa.Column('exception', sa.String(length=2048), nullable=True),
        sa.Column('start_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('user_id', sa.String(length=255), nullable=True),
        sa.Column('context', JSONB, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['test_run_id'], ['test_runs.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_request_logs_success', 'request_logs', ['success'])
    op.create_index('idx_request_logs_test_run_time', 'request_logs', ['test_run_id', 'start_time'])
    op.create_index('idx_request_logs_request_type_name', 'request_logs', ['request_type', 'name'])
    op.create_index(op.f('ix_request_logs_name'), 'request_logs', ['name'])
    op.create_index(op.f('ix_request_logs_request_type'), 'request_logs', ['request_type'])
    op.create_index(op.f('ix_request_logs_start_time'), 'request_logs', ['start_time'])
    op.create_index(op.f('ix_request_logs_test_run_id'), 'request_logs', ['test_run_id'])

    # Create failures table
    op.create_table(
        'failures',
        sa.Column('id', UUID(as_uuid=True), nullable=False),
        sa.Column('test_run_id', UUID(as_uuid=True), nullable=False),
        sa.Column('request_type', sa.String(length=10), nullable=False),
        sa.Column('name', sa.String(length=512), nullable=False),
        sa.Column('error_message', sa.String(length=2048), nullable=False),
        sa.Column('occurrences', sa.Integer(), nullable=False),
        sa.Column('first_occurrence', sa.DateTime(timezone=True), nullable=False),
        sa.Column('last_occurrence', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['test_run_id'], ['test_runs.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_failures_test_run_type_name', 'failures', ['test_run_id', 'request_type', 'name'])
    op.create_index(op.f('ix_failures_first_occurrence'), 'failures', ['first_occurrence'])
    op.create_index(op.f('ix_failures_name'), 'failures', ['name'])
    op.create_index(op.f('ix_failures_request_type'), 'failures', ['request_type'])
    op.create_index(op.f('ix_failures_test_run_id'), 'failures', ['test_run_id'])

    # Create stats_snapshots table
    op.create_table(
        'stats_snapshots',
        sa.Column('id', UUID(as_uuid=True), nullable=False),
        sa.Column('test_run_id', UUID(as_uuid=True), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('total_requests', sa.Integer(), nullable=False),
        sa.Column('failure_count', sa.Integer(), nullable=False),
        sa.Column('failure_rate', sa.Float(), nullable=False),
        sa.Column('avg_response_time', sa.Float(), nullable=False),
        sa.Column('median_response_time', sa.Float(), nullable=False),
        sa.Column('min_response_time', sa.Float(), nullable=False),
        sa.Column('max_response_time', sa.Float(), nullable=False),
        sa.Column('percentile_95', sa.Float(), nullable=False),
        sa.Column('percentile_99', sa.Float(), nullable=False),
        sa.Column('requests_per_second', sa.Float(), nullable=False),
        sa.Column('current_user_count', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['test_run_id'], ['test_runs.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_stats_snapshots_test_run_timestamp', 'stats_snapshots', ['test_run_id', 'timestamp'])
    op.create_index(op.f('ix_stats_snapshots_test_run_id'), 'stats_snapshots', ['test_run_id'])
    op.create_index(op.f('ix_stats_snapshots_timestamp'), 'stats_snapshots', ['timestamp'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('stats_snapshots')
    op.drop_table('failures')
    op.drop_table('request_logs')
    op.drop_table('test_runs')
