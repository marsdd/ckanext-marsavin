"""001 add extra packages fields

Revision ID: 09633cd45ad4
Revises: 
Create Date: 2019-11-25 10:46:06.670231

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '09633cd45ad4'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("package") as batch_op:
        batch_op.add_column(sa.Column("associated_tasks", sa.Text()))
        batch_op.add_column(sa.Column("collection_period", sa.Text()))
        batch_op.add_column(sa.Column("geographical_area", sa.Text()))
        batch_op.add_column(sa.Column("number_of_instances", sa.Text()))
        batch_op.add_column(sa.Column("number_of_missing_values", sa.Text()))
        batch_op.add_column(sa.Column("pkg_description", sa.Text()))
    pass


def downgrade():
    with op.batch_alter_table("package") as batch_op:
        batch_op.drop_column("associated_tasks")
        batch_op.drop_column("collection_period")
        batch_op.drop_column("geographical_area")
        batch_op.drop_column("number_of_instances")
        batch_op.drop_column("number_of_missing_values")
        batch_op.drop_column("pkg_description")
    pass
