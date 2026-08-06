"""add import job exercise id

Revision ID: 52a1c9d0e6b3
Revises: 41b2c3d4e5f7
Create Date: 2026-08-06 09:15:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '52a1c9d0e6b3'
down_revision = '41b2c3d4e5f7'
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.add_column('import_jobs', sa.Column('exercise_id', sa.Integer(), nullable=True))
    op.create_foreign_key(
        'fk_import_jobs_exercise_id_exercises',
        'import_jobs', 'exercises',
        ['exercise_id'], ['id'],
        ondelete='SET NULL',
    )

def downgrade() -> None:
    op.drop_constraint('fk_import_jobs_exercise_id_exercises', 'import_jobs', type_='foreignkey')
    op.drop_column('import_jobs', 'exercise_id')
