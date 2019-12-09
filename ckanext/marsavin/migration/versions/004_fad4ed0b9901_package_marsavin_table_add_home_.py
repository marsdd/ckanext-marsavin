"""004_package_marsavin_table_add_home_page_featured

Revision ID: fad4ed0b9901
Revises: cbbae47ebe2b
Create Date: 2019-11-25 10:49:13.840047

"""
from alembic import op
import sqlalchemy as sa
from ckan.migration import skip_based_on_legacy_engine_version


# revision identifiers, used by Alembic.
revision = 'fad4ed0b9901'
down_revision = 'cbbae47ebe2b'
branch_labels = None
depends_on = None


def upgrade():
    if skip_based_on_legacy_engine_version(op, __name__):
        return
    with op.batch_alter_table("package_marsavin") as batch_op:
        batch_op.create_foreign_key("fk_package_marsavin_packages",
                                    "package", ["package_id"], ["id"],
                                    ondelete="CASCADE")
    

def downgrade():
    with op.batch_alter_table("package_marsavin") as batch_op:
        batch_op.drop_constraint('fk_package_marsavin_packages')
