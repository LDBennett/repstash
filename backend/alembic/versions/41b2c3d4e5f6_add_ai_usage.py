"""add ai usage columns

Revision ID: 41b2c3d4e5f6
Revises: 31012346ee97
Create Date: 2026-08-05 22:40:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '41b2c3d4e5f6'
down_revision = '2d320ef25699'
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.add_column('users', sa.Column('ai_usage_count', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('users', sa.Column('last_ai_usage_date', sa.Date(), nullable=True))

def downgrade() -> None:
    op.drop_column('users', 'last_ai_usage_date')
    op.drop_column('users', 'ai_usage_count')
