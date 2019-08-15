# encoding: utf-8


def upgrade(migrate_engine):
    migrate_engine.execute(
        '''
        ALTER TABLE public.package_marsavin add constraint 
        fk_package_marsavin_packages FOREIGN KEY (package_id) REFERENCES 
        public.package (id) on delete cascade 
        '''
    )
