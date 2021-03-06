import ckan.plugins as plugins
from ckan.lib.plugins import DefaultTranslation
import ckan.plugins.toolkit as toolkit
from flask import Blueprint
import os
import logging
from .helpers import _mail_recipient, is_featured_organization, \
    get_homepage_featured_organizations, get_homepage_featured_groups, \
    get_package_resource_format_split, render_resource_format, \
    pages_build_main_nav
from . import actions, auth
from .cli import marsavin
from .views.request_access import RequestAccessView
from .views.marsavin import contact, terms, privacy, faq
from .views.pages import index as page_index, delete as \
    page_delete, read as page_read, CreatePagesView, EditPagesView

from .dictization import package_marsavin_save, package_marsavin_delete, \
    package_marsavin_load
from .model.package_marsavin import PackageMarsavin
import ckan.model as ckan_model
from ckan.lib.search import index_for
log = logging.getLogger("ckanext")


class MarsavinPlugin(plugins.SingletonPlugin, DefaultTranslation,
                     toolkit.DefaultDatasetForm):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IBlueprint)
    plugins.implements(plugins.ITranslation)
    plugins.implements(plugins.IDatasetForm)
    plugins.implements(plugins.ISession, inherit=True)
    plugins.implements(plugins.IActions)
    plugins.implements(plugins.IAuthFunctions)
    plugins.implements(plugins.IClick)

    # IActions
    def get_actions(self):
        return {
            u"format_autocomplete": actions.format_autocomplete,
            u"user_update": actions.user_update,
            u"marsavin_pages_new": actions.marsavin_pages_new,
            u"marsavin_pages_list": actions.marsavin_pages_list,
            u"marsavin_pages_show": actions.marsavin_pages_show,
            u"marsavin_pages_edit": actions.marsavin_pages_edit,
            u"marsavin_pages_delete": actions.marsavin_pages_delete,
            u"reqaccess_create": actions.reqaccess_create
        }

    # add template helper functions
    plugins.implements(plugins.ITemplateHelpers)

    # IConfigurer
    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('public/javascript', 'marsavin')
        toolkit.add_resource('public/css', 'marsavin')
        config_['ckan.favicon'] = "/images/avin.ico"
        
        redis_url = os.environ.get("CKAN_REDIS_URL", None)
        if redis_url:
            # ckan sessions in redis to allow for container idempotency
            config_['beaker.session.type'] = "ext:redis"
            config_['beaker.session.url'] = redis_url
            config_['beaker.session.timeout'] = 300
            
        relevant_env_vars = [
            'mailchimp_audience_id',
            'mailchimp_api_key'
        ]
        # environment variable based configurations
        for env_var in relevant_env_vars:
            config_[env_var] = os.environ.get(env_var, None)

    # IBlueprint - this is how we add additional routes to the app, only run
    # once when starting the app, cannot be changed afterwards
    def get_blueprint(self):
        blueprints = []
        bp = Blueprint(u'marsavin', self.__module__)
        util_rules = [
            (u'/contact', contact),
            (u'/terms', terms),
            (u'/privacy', privacy),
            (u'/faq', faq)
        ]
        for rule, view_func in util_rules:
            bp.add_url_rule(rule, view_func=view_func)

        blueprints.append(bp)

        pages_bp = Blueprint(u'marsavin_pages', self.__module__,
                             url_prefix=u"/pages")
        
        pages_bp.add_url_rule(u'/', view_func=page_index,
                              strict_slashes=False)
        pages_bp.add_url_rule(u'/new', methods=[u'GET', u'POST'],
                              view_func=CreatePagesView.as_view(
                                  "new"))
        pages_bp.add_url_rule(u'/edit/<page>', methods=[u'GET', u'POST'],
                              view_func=EditPagesView.as_view("edit"))
        pages_bp.add_url_rule(u'/delete/<page>', methods=[u'GET', u'POST'],
                              view_func=page_delete)
        pages_bp.add_url_rule(u'/<page>', view_func=page_read,
                              methods=[u"GET"])
            
        blueprints.append(pages_bp)

        reqacc_bp = Blueprint(u'request_access', self.__module__)
        reqacc_bp.add_url_rule("/request_access",
                               view_func=RequestAccessView.as_view(str(
                                   u'request_access')))
        
        blueprints.append(reqacc_bp)
        return blueprints

    def get_helpers(self):
        '''Register the most_popular_groups() function above as a template
        helper function.

        '''
        # Template helper function names should begin with the name of the
        # extension they belong to, to avoid clashing with functions from
        # other extensions.
        return {
            'is_featured_organization': is_featured_organization,
            'get_homepage_featured_organizations':
                get_homepage_featured_organizations,
            'get_homepage_featured_groups': get_homepage_featured_groups,
            'get_package_resource_format_split':
                get_package_resource_format_split,
            'render_resource_format': render_resource_format,
            'pages_build_main_nav': pages_build_main_nav
        }

    def _get_schema_updates(self, schema):
        schema.update({
            # a.s. validate maintainer fields aren't empty
            'maintainer': [toolkit.get_validator('not_empty'),
                           toolkit.get_validator('unicode_safe')],
            'maintainer_email': [toolkit.get_validator('not_empty'),
                                 toolkit.get_validator('unicode_safe'),
                                 toolkit.get_validator('email_validator')],
            # a.s. additional fields Jun 7, 2019
            'associated_tasks': [toolkit.get_validator('ignore_missing'),
                                 toolkit.get_validator('unicode_safe')],
            'collection_period': [toolkit.get_validator('ignore_missing'),
                                  toolkit.get_validator('unicode_safe')],
            'geographical_area': [toolkit.get_validator('ignore_missing'),
                                  toolkit.get_validator('unicode_safe')],
            'number_of_instances': [toolkit.get_validator('not_empty'),
                                    toolkit.get_validator('unicode_safe')],
            'pkg_description': [toolkit.get_validator('not_empty'),
                                toolkit.get_validator('unicode_safe')],
            'number_of_attributes': [toolkit.get_validator('unicode_safe')],
            'creation_date': [toolkit.get_validator('unicode_safe')],
            'expiry_date': [toolkit.get_validator('unicode_safe')],
            'has_missing_values': [toolkit.get_validator('boolean_validator')],
        })
        return schema

    def create_package_schema(self):
        # let's grab the default schema in our plugin
        schema = super(MarsavinPlugin, self).create_package_schema()

        return self._get_schema_updates(schema)

    def update_package_schema(self):
        # let's grab the default schema in our plugin
        schema = super(MarsavinPlugin, self).update_package_schema()

        return self._get_schema_updates(schema)

    def show_package_schema(self):
        # let's grab the default schema in our plugin
        schema = super(MarsavinPlugin, self).show_package_schema()

        return self._get_schema_updates(schema)

    def is_fallback(self):
        # Return True to register this plugin as the default handler for
        # package types not handled by any other IDatasetForm plugin.
        return True

    def package_types(self):
        # This plugin doesn't handle any special package types, it just
        # registers itself as the default (above).
        return []

    # ISession
    def before_commit(self, session):
        if not hasattr(session, '_object_cache'):
            return

        changed = session._object_cache["changed"]
        context = {
            "model": ckan_model
        }
        package_index = index_for(ckan_model.Package)

        for model_obj in set(changed):
            if not isinstance(model_obj, PackageMarsavin):
                continue
            log.debug("Changed Object: {the_object}".format(
                the_object=model_obj))
            package_id = model_obj.package_id
            pkg_dict = toolkit.get_action('package_show')(context,
                                                          {'id': package_id})
            # since we have an update on our secondary table, we want to send
            # this updated data to the search index
            log.info('Indexing just package %r...', pkg_dict['name'])
            package_index.remove_dict(pkg_dict)
            package_index.insert_dict(pkg_dict)

    def after_commit(self, session):
        pass
    
    def get_auth_functions(self):
        """
        returns the authorizations functions requred by some of the
        functionality in order to maintain the security of who can edit what
        in the system.  Mostly used by the dynamic page functionality.
        :return: dict
        """
        return {
            "ckanext_marsavin_pages_new": auth.pages_new,
            "ckanext_marsavin_pages_edit": auth.pages_edit,
            "ckanext_marsavin_pages_delete": auth.pages_delete,
            "ckanext_marsavin_pages_list": auth.pages_list,
            "ckanext_marsavin_pages_read": auth.pages_read
        }
    
    def get_commands(self):
        """
        Returns plugin commands
        :return: list
        """
        return [marsavin.marsavin]


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
        package_marsavin_save(pkg_dict, context)
        pass

    def after_update(self, context, pkg_dict):
        u'''
            Extensions will receive the validated data dict after the package
            has been updated (Note that the edit method will return a package
            domain object, which may not include all fields).
        '''
        package_marsavin_save(pkg_dict, context)
        pass

    def after_delete(self, context, pkg_dict):
        u'''
            Extensions will receive the data dict (tipically containing
            just the package id) after the package has been deleted.
        '''
        package_marsavin_delete(pkg_dict)
        pass

    def after_show(self, context, pkg_dict):
        u'''
            Extensions will receive the validated data dict after the package
            is ready for display (Note that the read method will return a
            package domain object, which may not include all fields).
        '''
        package_marsavin_load(pkg_dict)
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
        try:
            if pkg_dict['res_format']:
                updated_res_formats = []
                if pkg_dict['res_format'][0] != u"":
                    updated_res_formats = get_package_resource_format_split(
                        pkg_dict['res_format'])
                pkg_dict['res_format'] = updated_res_formats
        except KeyError:
            pass
        return pkg_dict

    def before_view(self, pkg_dict):
        u'''
             Extensions will recieve this before the dataset gets
             displayed. The dictionary passed will be the one that gets
             sent to the template.
        '''
        return pkg_dict
