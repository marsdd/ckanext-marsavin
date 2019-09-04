# encoding: utf-8


def upgrade(migrate_engine):
    migrate_engine.execute(
        '''
ALTER TABLE package
	ADD COLUMN IF NOT EXISTS associated_tasks text,
	ADD COLUMN IF NOT EXISTS collection_period text,
	ADD COLUMN IF NOT EXISTS geographical_area text,
	ADD COLUMN IF NOT EXISTS number_of_instances text,
	ADD COLUMN IF NOT EXISTS number_of_missing_values text,
	ADD COLUMN IF NOT EXISTS pkg_description text;


ALTER TABLE package_revision
	ADD COLUMN IF NOT EXISTS associated_tasks text,
	ADD COLUMN IF NOT EXISTS collection_period text,
	ADD COLUMN IF NOT EXISTS geographical_area text,
	ADD COLUMN IF NOT EXISTS number_of_instances text,
	ADD COLUMN IF NOT EXISTS number_of_missing_values text,
	ADD COLUMN IF NOT EXISTS pkg_description text;

        '''
    )
