"""Merge migration branches

Revision ID: e8ddfc204024
Revises: 2de26bce7d85, b3f1a2c4d5e6
Create Date: 2026-03-26 09:42:41.948494

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e8ddfc204024'
down_revision = ('2de26bce7d85', 'b3f1a2c4d5e6')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
