"""Create pages table

Revision ID: 5f84f3e6f555
Revises: 7d3575c1c41b
Create Date: 2020-07-22 15:41:56.716234

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from ckan.migration import skip_based_on_legacy_engine_version


# revision identifiers, used by Alembic.
revision = '5f84f3e6f555'
down_revision = '7d3575c1c41b'
branch_labels = None
depends_on = None


def upgrade():
    if skip_based_on_legacy_engine_version(op, __name__):
        pass

    op.create_table('ckanext_marsavin_pages',
                    sa.Column('id', postgresql.UUID(),
                              server_default=sa.text('uuid_generate_v4()'),
                              primary_key=True),
                    sa.Column('title', sa.Text),
                    sa.Column('name', sa.Text),
                    sa.Column('content', sa.Text),
                    sa.Column('lang', sa.Text),
                    sa.Column('sidebar_content', sa.Text),
                    sa.Column('order', sa.Text),
                    sa.Column('created', sa.TIMESTAMP),
                    sa.Column('modified', sa.TIMESTAMP),
                    sa.UniqueConstraint("name", "lang", name="u_name_lang")
                    )


def downgrade():
    op.drop_table("user_marsavin")
    pass
