from __future__ import print_function

# import sys
# from pprint import pprint

from ckan import model
import logging
# from ckan.logic import get_action, ValidationError
# from ckan.plugins import toolkit

from ckan.plugins.toolkit import CkanCommand
import migrate.versioning.api as mig
from ckanext.marsavin import migrate

log = logging.getLogger("ckanext_marsavin")


class DatabaseCommand(CkanCommand):
    '''Command to take care of MaRS Avin related things
        Usage:
          harvester initdb
            - Creates the necessary tables in the database
          harvester source {name} {url} {type} [{title}] [{active}] [{owner_org}] [{frequency}] [{config}]
            - create new harvest source
    '''

    summary = __doc__.split('\n')[0]
    usage = __doc__
    max_args = None
    min_args = None

    def __init__(self, name):
        super(DatabaseCommand, self).__init__(name)
        self.migrate_repository = migrate.__path__[0]

    def command(self):
        self._load_config()

        # We'll need a sysadmin user to perform most of the actions
        # We will use the sysadmin site user (named as the site_id)
        context = {'model': model, 'session': model.Session,
                   'ignore_auth': True}

        cmd = self.args[0]

        if cmd == "init":
            self.setup_migration_version_control()
            version_before = mig.db_version(model.meta.metadata.bind,
                                            self.migrate_repository)
            mig.upgrade(model.meta.metadata.bind, self.migrate_repository,
                        version=self.get_version())
            version_after = mig.db_version(model.meta.metadata.bind,
                                           self.migrate_repository)
            if version_after != version_before:
                log.info('CKAN database version upgraded: %s -> %s',
                         version_before, version_after)
            else:
                log.info('CKAN database version remains as: %s', version_after)
        else:
            print("bye")

    def setup_migration_version_control(self, version=None):
        import migrate.exceptions
        import migrate.versioning.api as mig
        # set up db version control (if not already)
        try:
            mig.version_control(model.meta.metadata.bind,
                                self.migrate_repository, version)
        except migrate.exceptions.DatabaseAlreadyControlledError:
            pass

    def get_version(self):
        try:
            version = self.args[1]
        except IndexError:
            version = None

        return version
