"""002 access request table plus marsavin table added

Revision ID: adc183cca9c4
Revises: 09633cd45ad4
Create Date: 2019-11-25 10:47:30.619605

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = 'adc183cca9c4'
down_revision = '09633cd45ad4'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')
    with op.batch_alter_table("package_marsavin") as batch_op:
        batch_op.add_column(sa.Column('id', postgresql.UUID(),
                            server_default=sa.text('uuid_generate_v4')))
        batch_op.add_column(sa.Column('package_id', sa.Text))
        batch_op.add_column(sa.Column('associated_tasks', sa.Text))
        batch_op.add_column(sa.Column('associated_tasks', sa.Text))
        batch_op.add_column(sa.Column('collection_period', sa.Text))
        batch_op.add_column(sa.Column('geographical_area', sa.Text))
        batch_op.add_column(sa.Column('number_of_instances', sa.Text))
        batch_op.add_column(sa.Column('number_of_missing_values', sa.Text))
        batch_op.add_column(sa.Column('pkg_description', sa.Text))
    pass


def downgrade():
    op.drop_table("package_marsavin")
    pass
