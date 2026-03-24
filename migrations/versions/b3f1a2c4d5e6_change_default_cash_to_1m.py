"""Change default cash from 100M to 1M

Revision ID: b3f1a2c4d5e6
Revises: 45a1e76293e5
Create Date: 2026-03-24 09:02:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'b3f1a2c4d5e6'
down_revision = '45a1e76293e5'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column(
            'cash',
            existing_type=sa.BigInteger(),
            server_default='1000000',
            existing_nullable=True
        )


def downgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column(
            'cash',
            existing_type=sa.BigInteger(),
            server_default='100000000',
            existing_nullable=True
        )
