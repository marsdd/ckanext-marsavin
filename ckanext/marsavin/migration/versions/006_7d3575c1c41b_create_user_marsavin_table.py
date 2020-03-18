"""create user marsavin table

Revision ID: 7d3575c1c41b
Revises: ddbfb0dc008d
Create Date: 2020-03-18 10:31:33.687075

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from ckan.migration import skip_based_on_legacy_engine_version

# revision identifiers, used by Alembic.
revision = '7d3575c1c41b'
down_revision = 'ddbfb0dc008d'
branch_labels = None
depends_on = None


def upgrade():
    if skip_based_on_legacy_engine_version(op, __name__):
        return
    op.create_table('user_marsavin',
                    sa.Column('id', postgresql.UUID(),
                              server_default=sa.text('uuid_generate_v4')),
                    sa.Column('user_id', sa.Text),
                    sa.Column('allow_marketting_emails', sa.Text)
                    )

def downgrade():
    op.drop_table("user_marsavin")
