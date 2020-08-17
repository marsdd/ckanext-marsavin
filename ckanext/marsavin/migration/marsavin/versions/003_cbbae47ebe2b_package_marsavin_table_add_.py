"""003_package_marsavin_table_add_additional_fields

Revision ID: cbbae47ebe2b
Revises: adc183cca9c4
Create Date: 2019-11-25 10:48:20.077231

"""
from alembic import op
import sqlalchemy as sa
from ckan.migration import skip_based_on_legacy_engine_version


# revision identifiers, used by Alembic.
revision = 'cbbae47ebe2b'
down_revision = 'adc183cca9c4'
branch_labels = None
depends_on = None


def upgrade():
    if skip_based_on_legacy_engine_version(op, __name__):
        return
    with op.batch_alter_table("package_marsavin") as batch_op:
        batch_op.add_column(sa.Column("number_of_attributes", sa.Text()))
        batch_op.add_column(sa.Column("creation_date", sa.Date()))
        batch_op.add_column(sa.Column("expiry_date", sa.Date()))
        batch_op.add_column(sa.Column("has_missing_values", sa.Boolean()))
        batch_op.create_unique_constraint('package_id_unique', 'package_id')


def downgrade():
    with op.batch_alter_table("package_marsavin") as batch_op:
        batch_op.drop_column("number_of_attributes")
        batch_op.drop_column("creation_date")
        batch_op.drop_column("expiry_date")
        batch_op.drop_column("has_missing_values")
        batch_op.drop_constraint('package_id_unique')
