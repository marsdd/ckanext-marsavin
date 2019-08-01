from __future__ import print_function

# import sys
# from pprint import pprint

from ckan import model
# from ckan.logic import get_action, ValidationError
# from ckan.plugins import toolkit

from ckan.lib.cli import CkanCommand
from pprint import pprint


class MarsavinCommand(CkanCommand):
    '''Command to take care of mar's avin related things
        Usage:
          harvester initdb
            - Creates the necessary tables in the database
          harvester source {name} {url} {type} [{title}] [{active}] [{owner_org}] [{frequency}] [{config}]
            - create new harvest source
    '''

    def __init__(self, name):
        super(MarsavinCommand, self).__init__(name)

    def command(self):
        self._load_config()

        # We'll need a sysadmin user to perform most of the actions
        # We will use the sysadmin site user (named as the site_id)
        context = {'model': model, 'session': model.Session,
                   'ignore_auth': True}


        pprint(self)
