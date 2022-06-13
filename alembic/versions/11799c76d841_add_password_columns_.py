"""Add password to visitor

Revision ID: 11799c76d841
Revises: 
Create Date: 2022-06-12 14:15:30.851158

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '11799c76d841'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("voters", sa.Column("password", sa.String))


def downgrade() -> None:
    op.drop_column("voters", "password")
