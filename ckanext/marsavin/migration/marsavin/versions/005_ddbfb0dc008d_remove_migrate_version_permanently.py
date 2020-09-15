"""Remove migrate version permanently

Revision ID: ddbfb0dc008d
Revises: fad4ed0b9901
Create Date: 2019-12-09 14:21:31.220771

"""
from alembic import op
import sqlalchemy as sa
from ckan.migration import skip_based_on_legacy_engine_version
from os import path


# revision identifiers, used by Alembic.
revision = 'ddbfb0dc008d'
down_revision = 'fad4ed0b9901'
branch_labels = None
depends_on = None


def upgrade():
    if skip_based_on_legacy_engine_version(op, __name__):
        return
    op.drop_table('migrate_version')
    pass


def downgrade():
    migrate_path = path.dirname(op.context.config.get_main_option(
        "script_location")) + "migrate"
    previous_version = int(__name__.split(u'_', 1)[0]) - 1
    migrate_version_table = op.create_table(
        'migrate_version',
            sa.Column('repository_id', sa.Unicode(length=250), nullable=False),
            sa.Column('package_id', sa.Text()),
            sa.Column('associated_tasks', sa.Integer()),
        )
    op.bulk_insert(
        migrate_version_table,
        [
            {
                "repository_id": "ckanext_marsavin",
                "repository_path": migrate_path,
                "version": previous_version
            }
        ]
    )
    pass
