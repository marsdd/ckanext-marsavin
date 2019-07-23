import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from flask import Blueprint
import os
import logging
from helpers import _mail_recipient
import actions
from views.request_access import RequestAccessView
log = logging.getLogger(__name__)


class MarsavinPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)

    # IConfigurer
    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'marsavin')


class MarsavinRequestAccessPlugin(plugins.SingletonPlugin,
                                  toolkit.DefaultDatasetForm):
    plugins.implements(plugins.IActions)
    plugins.implements(plugins.IDatasetForm)
    plugins.implements(plugins.IBlueprint)

    # IActions
    def get_actions(self):
        return {
            "ckanext_marsavin_reqaccess_create": actions.reqaccess_create
        }

    def create_package_schema(self):
        # let's grab the default schema in our plugin
        schema = super(MarsavinRequestAccessPlugin,
                        self).create_package_schema()

        schema.update({
            # a.s. validate maintainer fields aren't empty
            'maintainer': [toolkit.get_validator('not_empty'),
                            toolkit.get_validator('unicode_safe')],
            'maintainer_email': [toolkit.get_validator('not_empty'),
                           toolkit.get_validator('unicode_safe')],
            # a.s. additional fields Jun 7, 2019
            'associated_tasks': [toolkit.get_validator('ignore_missing'),
                           toolkit.get_validator('unicode_safe')],
            'collection_period': [toolkit.get_validator('ignore_missing'),
                           toolkit.get_validator('unicode_safe')],
            'geographical_area': [toolkit.get_validator('ignore_missing'),
                           toolkit.get_validator('unicode_safe')],
            'number_of_instances': [toolkit.get_validator('not_empty'),
                           toolkit.get_validator('unicode_safe')],
            'number_of_missing_values': [toolkit.get_validator(
                 'ignore_missing'),
                           toolkit.get_validator('unicode_safe')],
            'pkg_description': [toolkit.get_validator('not_empty'),
                           toolkit.get_validator('unicode_safe')],
        })
        return schema

    def is_fallback(self):
        # Return True to register this plugin as the default handler for
        # package types not handled by any other IDatasetForm plugin.
        return True

    def package_types(self):
        # This plugin doesn't handle any special package types, it just
        # registers itself as the default (above).
        return []

    # IBlueprint
    def get_blueprint(self):
        bp = Blueprint(u'req_access', self.__module__)
        bp.add_url_rule("/request_access",
                        view_func=RequestAccessView.as_view(str(
                            u'request_access')))
        return bp


class MarsavinResourcePlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IResourceController)

    # IResourceController
    def after_create(self, context, resource):
        # a.s. send a msg to OCE distribution group
        recipient = {}
        email_context = context['package']
        email_resource = email_context.resources[-1]
        email_dict = {
            "subject": u'AVIN Resource has been added',
            "body": u'New Resource has been created: ' + '\n\n' + \
                    u'--------------------------------' + '\n' + \
                    u'Package Name: ' + email_context.name + '\n' + \
                    u'Package Title: ' + email_context.title + '\n' + \
                    u'Package Author: ' + email_context.author + '\n' + \
                    u'Package Maintainer: ' + email_context.maintainer + \
                    '\n' + \
                    u'Package Notes: ' + email_context.notes + '\n' + \
                    u'--------------------------------' + '\n' + \
                    u'Resource Name: ' + email_resource.name + '\n' + \
                    u'Resource URL: ' + email_resource.url + '\n' + \
                    u'Resource Description: ' + email_resource.description + \
                    '\n' + \
                    u'--------------------------------' + '\n'
        }

        recipient['display_name'] = os.environ['oce_email_distribution_group']
        recipient['email'] = os.environ['oce_email_distribution_group']

        toolkit.enqueue_job(_mail_recipient, [recipient, email_dict])

        log.info(
            'create.py.resource_create: a.s. - email to OCE distribution '
            'group sent')

    def before_create(self, context, resource):
        u'''
        Extensions will receive this before a resource is created.

        :param context: The context object of the current request, this
            includes for example access to the ``model`` and the ``user``.
        :type context: dictionary
        :param resource: An object representing the resource to be added
            to the dataset (the one that is about to be created).
        :type resource: dictionary
        '''
        pass

    def before_update(self, context, current, resource):
        u'''
        Extensions will receive this before a resource is updated.

        :param context: The context object of the current request, this
            includes for example access to the ``model`` and the ``user``.
        :type context: dictionary
        :param current: The current resource which is about to be updated
        :type current: dictionary
        :param resource: An object representing the updated resource which
            will replace the ``current`` one.
        :type resource: dictionary
        '''
        pass

    def after_update(self, context, resource):
        u'''
        Extensions will receive this after a resource is updated.

        :param context: The context object of the current request, this
            includes for example access to the ``model`` and the ``user``.
        :type context: dictionary
        :param resource: An object representing the updated resource in
            the dataset (the one that was just updated). As with
            ``after_create``, a noteworthy key in the resource dictionary
            ``url_type`` which is set to ``upload`` when the resource file
            is uploaded instead of linked.
        :type resource: dictionary
        '''
        pass

    def before_delete(self, context, resource, resources):
        u'''
        Extensions will receive this before a previously created resource is
        deleted.

        :param context: The context object of the current request, this
            includes for example access to the ``model`` and the ``user``.
        :type context: dictionary
        :param resource: An object representing the resource that is about
            to be deleted. This is a dictionary with one key: ``id`` which
            holds the id ``string`` of the resource that should be deleted.
        :type resource: dictionary
        :param resources: The list of resources from which the resource will
            be deleted (including the resource to be deleted if it existed
            in the package).
        :type resources: list
        '''
        pass

    def after_delete(self, context, resources):
        u'''
        Extensions will receive this after a previously created resource is
        deleted.

        :param context: The context object of the current request, this
            includes for example access to the ``model`` and the ``user``.
        :type context: dictionary
        :param resources: A list of objects representing the remaining
            resources after a resource has been removed.
        :type resource: list
        '''
        pass

    def before_show(self, resource_dict):
        u'''
        Extensions will receive the validated data dict before the resource
        is ready for display.

        Be aware that this method is not only called for UI display, but also
        in other methods like when a resource is deleted because showing a
        package is used to get access to the resources in a package.
        '''
        return resource_dict


class MarsavinPackagePlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IPackageController)

    def create(self, entity):
        # a.s. send a msg to OCE distribution group
        recipient = {}
        email_dict = {
            "subject": u'AVIN Dataset has been added',
            "body":  u'New Dataset has been created: ' + '\n\n' +
                     u'--------------------------------' + '\n' +
                     u'Package Name: ' + entity.name + '\n' +
                     u'Package Title: ' + entity.title + '\n' +
                     u'Package Author: ' + entity.author + '\n' +
                     u'Package Maintainer: ' + entity.maintainer + '\n' +
                     u'Package Notes: ' + entity.notes + '\n' +
                     u'--------------------------------' + '\n'
        }
        recipient['display_name'] = os.environ['oce_email_distribution_group']
        recipient['email'] = os.environ['oce_email_distribution_group']

        toolkit.enqueue_job(_mail_recipient, [recipient, email_dict])

        log.info(
            'create.py.package_create: a.s. - email to OCE distribution '
            'group sent - s.h. moved to plugin')

    def read(self, entity):
        u'''Called after IGroupController.before_view inside package_read.
        '''
        pass

    def edit(self, entity):
        u'''Called after group had been updated inside package_update.
        '''
        pass

    def delete(self, entity):
        u'''Called before commit inside package_delete.
        '''
        pass

    def after_create(self, context, pkg_dict):
        u'''
            Extensions will receive the validated data dict after the package
            has been created (Note that the create method will return a package
            domain object, which may not include all fields). Also the newly
            created package id will be added to the dict.
        '''
        pass

    def after_update(self, context, pkg_dict):
        u'''
            Extensions will receive the validated data dict after the package
            has been updated (Note that the edit method will return a package
            domain object, which may not include all fields).
        '''
        pass

    def after_delete(self, context, pkg_dict):
        u'''
            Extensions will receive the data dict (tipically containing
            just the package id) after the package has been deleted.
        '''
        pass

    def after_show(self, context, pkg_dict):
        u'''
            Extensions will receive the validated data dict after the package
            is ready for display (Note that the read method will return a
            package domain object, which may not include all fields).
        '''
        pass

    def before_search(self, search_params):
        u'''
            Extensions will receive a dictionary with the query parameters,
            and should return a modified (or not) version of it.

            search_params will include an `extras` dictionary with all values
            from fields starting with `ext_`, so extensions can receive user
            input from specific fields.

        '''
        return search_params

    def after_search(self, search_results, search_params):
        u'''
            Extensions will receive the search results, as well as the search
            parameters, and should return a modified (or not) object with the
            same structure:

                {'count': '', 'results': '', 'facets': ''}

            Note that count and facets may need to be adjusted if the extension
            changed the results for some reason.

            search_params will include an `extras` dictionary with all values
            from fields starting with `ext_`, so extensions can receive user
            input from specific fields.

        '''

        return search_results

    def before_index(self, pkg_dict):
        u'''
             Extensions will receive what will be given to the solr for
             indexing. This is essentially a flattened dict (except for
             multli-valued fields such as tags) of all the terms sent to
             the indexer. The extension can modify this by returning an
             altered version.
        '''
        return pkg_dict

    def before_view(self, pkg_dict):
        u'''
             Extensions will recieve this before the dataset gets
             displayed. The dictionary passed will be the one that gets
             sent to the template.
        '''
        return pkg_dict
