"""added agreement answers to the database

Revision ID: 04bdff468b5d
Revises: 5f84f3e6f555
Create Date: 2020-10-06 16:45:09.927146

"""
from alembic import op
import sqlalchemy as sa
from ckan.migration import skip_based_on_legacy_engine_version


# revision identifiers, used by Alembic.
revision = '04bdff468b5d'
down_revision = '5f84f3e6f555'
branch_labels = None
depends_on = None


def upgrade():
    if skip_based_on_legacy_engine_version(op, __name__):
        return
    with op.batch_alter_table("user_marsavin") as batch_op:
        batch_op.add_column(sa.Column("user-terms-agree", sa.Text()))
        batch_op.add_column(sa.Column("uploader-terms-agree", sa.Text()))
    pass


def downgrade():
    with op.batch_alter_table("user_marsavin") as batch_op:
        batch_op.drop_column("user-terms-agree")
        batch_op.drop_column("uploader-terms-agree")
    pass
