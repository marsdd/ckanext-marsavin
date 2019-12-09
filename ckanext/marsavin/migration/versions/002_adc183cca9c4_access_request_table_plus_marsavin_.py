"""002 access request table plus marsavin table added

Revision ID: adc183cca9c4
Revises: 09633cd45ad4
Create Date: 2019-11-25 10:47:30.619605

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from ckan.migration import skip_based_on_legacy_engine_version


# revision identifiers, used by Alembic.
revision = 'adc183cca9c4'
down_revision = '09633cd45ad4'
branch_labels = None
depends_on = None


def upgrade():
    if skip_based_on_legacy_engine_version(op, __name__):
        return
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')
    op.create_table('package_marsavin',
        sa.Column('id', postgresql.UUID(), server_default=sa.text(
            'uuid_generate_v4')),
        sa.Column('package_id', sa.Text),
        sa.Column('associated_tasks', sa.Text),
        sa.Column('associated_tasks', sa.Text),
        sa.Column('collection_period', sa.Text),
        sa.Column('geographical_area', sa.Text),
        sa.Column('number_of_instances', sa.Text),
        sa.Column('number_of_missing_values', sa.Text),
        sa.Column('pkg_description', sa.Text)
    )

    op.create_table('access_request',
        sa.Column('id', sa.Text, server_default=sa.text(
            'uuid_generate_v4'), nullable=False),
        sa.Column('user_ip_address', sa.Text),
        sa.Column('user_email', sa.Text),
        sa.Column('maintainer_name', sa.Text),
        sa.Column('maintainer_email', sa.Text),
        sa.Column('user_msg', sa.Text),
        sa.Column('created', sa.TIMESTAMP, server_default=sa.func.now()),
    )


def downgrade():
    op.drop_table("package_marsavin")
    op.drop_table("access_request")
