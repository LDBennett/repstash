"""add thumbnail url

Revision ID: 41b2c3d4e5f7
Revises: 41b2c3d4e5f6
Create Date: 2026-08-05 22:58:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '41b2c3d4e5f7'
down_revision = '41b2c3d4e5f6'
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.add_column('exercises', sa.Column('thumbnail_url', sa.String(), nullable=True))

def downgrade() -> None:
    op.drop_column('exercises', 'thumbnail_url')
