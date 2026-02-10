"""Initial schema - Employee and Duty tables

Revision ID: 001
Revises: 
Create Date: 2026-01-22 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create employees table
    op.create_table(
        'employees',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('telegram_id', sa.BIGINT(), nullable=False),
        sa.Column('username', sa.String(length=255), nullable=True),
        sa.Column('full_name', sa.String(length=255), nullable=False),
        sa.Column('is_admin', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint('id', name='pk_employees'),
        sa.UniqueConstraint('telegram_id', name='uq_employees_telegram_id'),
    )
    op.create_index(
        'ix_employees_telegram_id', 'employees', ['telegram_id'], unique=True
    )

    # Create duties table
    op.create_table(
        'duties',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('employee_id', sa.Integer(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('notified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint('id', name='pk_duties'),
        sa.ForeignKeyConstraint(
            ['employee_id'],
            ['employees.id'],
            name='fk_duties_employee',
            ondelete='CASCADE',
        ),
        sa.UniqueConstraint('date', name='uq_duties_date'),
    )
    op.create_index('ix_duties_date', 'duties', ['date'], unique=True)
    op.create_index('ix_duties_employee_id', 'duties', ['employee_id'], unique=False)


def downgrade() -> None:
    # Drop duties table
    op.drop_index('ix_duties_employee_id', table_name='duties')
    op.drop_index('ix_duties_date', table_name='duties')
    op.drop_table('duties')

    # Drop employees table
    op.drop_index('ix_employees_telegram_id', table_name='employees')
    op.drop_table('employees')
