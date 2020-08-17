from __future__ import print_function

# import sys
# from pprint import pprint

from ckan import model
import logging
import datetime
# from ckan.logic import get_action, ValidationError
# from ckan.plugins import toolkit

from ckan.plugins.toolkit import CkanCommand, get_action, _, config
from ckan.model import meta
import migrate.versioning.api as mig
from ckanext.marsavin import migration
from ckanext.marsavin.model.package_marsavin import PackageMarsavin
from ckan.lib.search import rebuild
from alembic.config import Config
from sqlalchemy.exc import ProgrammingError
from alembic.command import (
    upgrade as alembic_upgrade,
    downgrade as alembic_downgrade,
    current as alembic_current
)
from alembic.config import Config as AlembicConfig

log = logging.getLogger(__name__)


class DatabaseCommand(CkanCommand):
    '''Command to take care of MaRS Avin Database migrations
        Usage:
          paster --plugin=ckanext-marsavin db init
            - Creates the necessary tables in the database
          harvester source {name} {url} {type} [{title}] [{active}] [{owner_org}] [{frequency}] [{config}]
            - create new harvest source
    '''

    summary = __doc__.split('\n')[0]
    usage = __doc__
    max_args = None
    min_args = None

    def __init__(self, name):
        self.alembic_config = Config()
        super(DatabaseCommand, self).__init__(name)
        self.migrate_repository = migration.__path__[0]
        self._alembic_output = []
            
    def command(self):
        '''Upgrade db using sqlalchemy migrations.

        @param version: version to upgrade to (if None upgrade to latest)
        '''
        self._load_config()
        version = self.get_version()
        _assert_engine_msg = (
                                 u'Database migration - only Postgresql engine supported (not %s).'
                             ) % meta.engine.name
        assert meta.engine.name in (
            u'postgres', u'postgresql'
        ), _assert_engine_msg
        self.setup_migration_version_control()
        version_before = self.current_version()
        alembic_upgrade(self.alembic_config, version)
        version_after = self.current_version()
    
        if version_after != version_before:
            log.info(
                u'CKAN database version upgraded: %s -> %s',
                version_before,
                version_after
            )
        else:
            log.info(u'CKAN database version remains as: %s',
                     version_after)

    def setup_migration_version_control(self):
        self.reset_alembic_output()
        alembic_config = AlembicConfig()
        alembic_config.set_main_option(
            "script_location", self.migrate_repository
        )
        alembic_config.set_main_option(
            "sqlalchemy.url", str(meta.metadata.bind.url)
        )
        try:
            sqlalchemy_migrate_version = meta.metadata.bind.execute(
                u'select version from migrate_version'
            ).scalar()
        except ProgrammingError:
            sqlalchemy_migrate_version = 0
    
        # this value is used for graceful upgrade from
        # sqlalchemy-migrate to alembic
        alembic_config.set_main_option(
            "sqlalchemy_migrate_version", str(sqlalchemy_migrate_version)
        )
        # This is an interceptor for alembic output. Otherwise,
        # everything will be printed to stdout
        alembic_config.print_stdout = self.add_alembic_output
    
        self.alembic_config = alembic_config

    def get_version(self):
        try:
            version = self.args[1]
        except IndexError:
            version = 'head'

        return version
    
    def current_version(self):
        try:
            alembic_current(self.alembic_config)
            return self.take_alembic_output()[0][0]
        except (TypeError, IndexError):
            # alembic is not initialized yet
            return 'base'
    
    def reset_alembic_output(self):
        self._alembic_output = []

    def add_alembic_output(self, *args):
        self._alembic_output.append(args)

    def take_alembic_output(self, with_reset=True):
        output = self._alembic_output
        if with_reset:
            self.reset_alembic_output()
        return output


class PackageCommand(CkanCommand):
    '''Command to take care of MaRS Avin search schema migrations
        Usage:
          paster --plugin=ckanext-marsavin package update_search_schema
            - Creates the necessary tables in the database
          harvester source {name} {url} {type} [{title}] [{active}] [{owner_org}] [{frequency}] [{config}]
            - create new harvest source
    '''

    summary = __doc__.split('\n')[0]
    usage = __doc__
    max_args = None
    min_args = None

    def __init__(self, name):
        super(PackageCommand, self).__init__(name)

    def command(self):
        self._load_config()

        cmd = self.args[0]

        if cmd == "delete_expired":
            query = model.Session.query(model.Package, PackageMarsavin).filter(
                model.Package.id == PackageMarsavin.package_id
            ).filter(
                model.Package.state == "active"
            ).filter(
                PackageMarsavin.expiry_date < datetime.date.today()
            )

            expired_packages = query.all()

            if expired_packages:
                rev = model.repo.new_revision()
                rev.message = _(u'CLI Command: Delete expired Packages')
                for package in expired_packages:
                    # model.package
                    package[0].delete()
                    rebuild(package[0].id)

            model.repo.commit()

        elif cmd == "update_search_schema":
            from ckan.lib.search.common import make_connection
            fields = {
                "associated_tasks": b'{"add-field":{"name": '
                                    b'"associated_tasks",  "type": "textgen", '
                                    b'"indexed": "true", stored: "true"}}',
                "collection_period": b'{"add-field":{"name": '
                                    b'"collection_period",  "type": "textgen", '
                                    b'"indexed": "true", stored: "true"}}',
                "geographical_area": b'{"add-field":{"name": '
                                    b'"geographical_area",  "type": "textgen", '
                                    b'"indexed": "true", stored: "true"}}',
                "number_of_instances": b'{"add-field":{"name": '
                                    b'"number_of_instances",  '
                                       b'"type": "textgen", '
                                    b'"indexed": "true", stored: "true"}}',
                "number_of_attributes": b'{"add-field":{"name": '
                                    b'"number_of_attributes",  '
                                        b'"type": "textgen", '
                                    b'"indexed": "true", stored: "true"}}',
                "pkg_description": b'{"add-field":{"name": '
                                    b'"pkg_description",  "type": "textgen", '
                                    b'"indexed": "true", stored: "true"}}',
                "creation_date": b'{"add-field":{"name": '
                                    b'"creation_date",  "type": "date", '
                                    b'"indexed": "true", stored: "true"}}',
                "expiry_date": b'{"add-field":{"name": '
                                    b'"expiry_date",  "type": "date", '
                                    b'"indexed": "true", stored: "true"}}',
                "has_missing_values": b'{"add-field":{"name": '
                                    b'"has_missing_values",  '
                                      b'"type": "boolean", '
                                    b'"indexed": "true", stored: "true"}}',
            }

            copy_fields = {
                "associated_tasks": b'{"add-copy-field":{"source": '
                                    b'"associated_tasks",  "dest": "text"}}',
                "collection_period": b'{"add-copy-field":{"source": '
                                    b'"collection_period",  "dest": "text"}}',
                "geographical_area": b'{"add-copy-field":{"source": '
                                    b'"geographical_area",  "dest": "text"}}',
                "pkg_description": b'{"add-copy-field":{"source": '
                                    b'"pkg_description",  "dest": "text"}}'
            }

            conn = make_connection()
            path = "schema"
            for fieldname in fields:
                res = conn._send_request("post", path, fields[fieldname])
                log.debug("Result of update {result}".format(result=res))

            for fieldname in copy_fields:
                res = conn._send_request("post", path, copy_fields[fieldname])
                log.debug("Result of update {result}".format(result=res))
            pass
