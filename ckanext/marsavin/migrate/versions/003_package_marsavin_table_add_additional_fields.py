# encoding: utf-8


def upgrade(migrate_engine):
    migrate_engine.execute(
        '''
        ALTER TABLE public.package_marsavin add column if not exists number_of_attributes text;
        ALTER TABLE public.package_marsavin add column if not exists creation_date date;
        ALTER TABLE public.package_marsavin add column if not exists expiry_date date;
        ALTER TABLE public.package_marsavin add column if not exists has_missing_values boolean;
        ALTER TABLE public.package_marsavin ADD CONSTRAINT if not exists package_id_unique unique (package_id);
        '''
    )
