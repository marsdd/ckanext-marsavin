from .helpers import _mail_recipient, get_package_resource_format_split, \
    subscribe_to_mailchimp
import ckan.logic as logic
from ckanext.marsavin.dictization import reqaccess_dict_save, \
    marsavin_pages_dictize
import logging
from ckan.plugins import toolkit
from ckanext.marsavin.schema import default_reqaccess_schema, \
    default_update_user_schema, marsavin_pages_new_schema, \
    marsavin_pages_edit_schema
import sqlalchemy
from sqlalchemy import text
import ckan.logic.schema as schema_
import ckan.lib.dictization.model_dictize as model_dictize
import ckan.lib.dictization.model_save as model_save
from .dictization import user_marsavin_save
from ckanext.marsavin.model.marsavin_pages import MarsavinPages
import ckan.lib.dictization as d

log = logging.getLogger(__name__)

_func = sqlalchemy.func
_and_ = sqlalchemy.and_

# Define some shortcuts
# Ensure they are module-private so that they don't get loaded as available
# actions in the action API.
_validate = toolkit.navl_validate
_check_access = toolkit.check_access
_get_action = toolkit.get_action
ValidationError = toolkit.ValidationError
NotFound = toolkit.ObjectNotFound
_get_or_bust = toolkit.get_or_bust

log = logging.getLogger(__name__)


# a.s.
def reqaccess_create(context, data_dict):
    ''' Create a new access request.

    :param id: the id of the new requestor (optional, not recommended, auto-generate)
    :type id: string
    :param user_ip_address: the ip address of the requestor
    :type user_ip_address: string
    :param maintainer_name: the maintainer's name
    :type maintainer_name: string
    :param maintainer_email: the email address for the maintainer
    :type maintainer_email: string
    :param user_msg: a message to the maintainer from the requestor (optional)
    :type user_msg: string

    :returns: the newly created request access
    :rtype: dictionary

    # a.s. end of the section

    '''

    model = context['model']
    # schema = context.get('schema') or ckan.logic.schema.default
    # reqaccess_schema()
    schema = default_reqaccess_schema()
    session = context['session']

    data, errors = _validate(data_dict, schema, context)

    if errors:
        for er in errors:
            log.info(
                'Validation errors in create.py a.s. - {er}'.format(er=er))

        session.rollback()
        raise ValidationError(errors)

    reqaccess_dict_save(data, context)

    if not context.get('defer_commit'):
        model.repo.commit()
        log.info('create.py: a.s. - access request committed to the db')

    # a.s.
    recipient = {
        "display_name": data_dict['maintainer_name'],
        "email": data_dict['maintainer_email']
    }
    email_dict = {
        "subject": data_dict['subject'],
        "body": u'Requestor\'s Email: ' + \
        data_dict['user_email'] + '\n' + \
        u'Resource Name: ' + \
        data_dict['resource_name'] + \
        '\n\nMessage:\n' + data_dict['user_msg']
    }

    toolkit.enqueue_job(_mail_recipient, [recipient, email_dict])
    log.info('create.py: a.s. - email to a maintainer enqueued')

    return data_dict


@logic.validate(logic.schema.default_autocomplete_schema)
def format_autocomplete(context, data_dict):
    '''Return a list of resource formats whose names contain a string.
    it overrides the default in order to modify the output for
    multi format per resource instead of a single format per resource.

    :param q: the string to search for
    :type q: string
    :param limit: the maximum number of resource formats to return (optional,
        default: ``5``)
    :type limit: int

    :rtype: list of strings

    '''
    model = context['model']
    session = context['session']

    _check_access('format_autocomplete', context, data_dict)

    q = data_dict['q']
    limit = data_dict.get('limit', 5)

    like_q = u'%' + q + u'%'

    query = (session.query(
        model.Resource.format,
        _func.count(model.Resource.format).label('total'))
        .filter(_and_(
            model.Resource.state == 'active',
        ))
        .filter(model.Resource.format.ilike(like_q))
        .group_by(model.Resource.format)
        .order_by(text('total DESC'))
        .limit(limit))

    # We want to split the csv items for the resources into individual list
    # items
    output_list = get_package_resource_format_split(
        [resource.format.lower() for resource in query]
    )

    # We need to make sure the output matches the query as we are extracting
    # the value post database query
    output_list = list(filter(lambda format_string: q.lower() in format_string,
                              output_list))
    return output_list


def user_update(context, data_dict):
    '''Update a user account.

    Normal users can only update their own user accounts. Sysadmins can update
    any user account. Can not modify exisiting user's name.

    For further parameters see
    :py:func:`~ckan.logic.action.create.user_create`.

    :param id: the name or id of the user to update
    :type id: string

    :returns: the updated user account
    :rtype: dictionary

    '''
    model = context['model']
    session = context['session']
    schema = context.get('schema') or default_update_user_schema()
    id = _get_or_bust(data_dict, 'id')
    
    data_dict['user-terms-agree'] = toolkit.request.form.get("user-terms-agree")
    data_dict['uploader-terms-agree'] = toolkit.request.form.get(
        "uploader-terms-agree")
    data_dict['allow_marketting_emails'] = toolkit.request.form.get(
        "allow_marketting_emails")
    
    user_obj = model.User.get(id)
    context['user_obj'] = user_obj
    if user_obj is None:
        raise NotFound('User was not found.')

    _check_access('user_update', context, data_dict)

    data, errors = _validate(data_dict, schema, context)
    if errors:
        session.rollback()
        raise ValidationError(errors)

    # user state of "pending" is the user who doesn't yet have access to the
    # site and must reset their password to do so.
    if user_obj.state == u'pending' and not (
        data['user-terms-agree'] and data['uploader-terms-agree']
    ):
        session.rollback()
        raise ValueError(toolkit._("You must agree to the Terms and "
                                   "Conditions and Uploader Agreement"))

    # user schema prevents non-sysadmins from providing password_hash
    if 'password_hash' in data:
        data['_password'] = data.pop('password_hash')

    user = model_save.user_dict_save(data, context)
    user_marsavin = user_marsavin_save(data, context)
    try:
        if data["allow_marketting_emails"]:
            toolkit.enqueue_job(subscribe_to_mailchimp, [user_obj])
    except KeyError:
        pass
        

    activity_dict = {
            'user_id': user.id,
            'object_id': user.id,
            'activity_type': 'changed user',
            }
    activity_create_context = {
        'model': model,
        'user': user,
        'defer_commit': True,
        'ignore_auth': True,
        'session': session
    }
    _get_action('activity_create')(activity_create_context, activity_dict)
    # TODO: Also create an activity detail recording what exactly changed in
    # the user.

    if not context.get('defer_commit'):
        model.repo.commit()
    return model_dictize.user_dictize(user, context)


def marsavin_pages_save(context, data_dict):
    schema = context["schema"]
    model = context["model"]
    session = context["session"]
    marsavin_page_dict, errors = _validate(data=data_dict, schema=schema,
                                           context=context)
    
    if errors:
        raise ValidationError(errors)
    
    marsavin_page = d.table_dict_save(marsavin_page_dict, MarsavinPages,
                                      context)
    
    # generate the user id
    session.flush()
    
    if not context.get('defer_commit'):
        try:
            model.repo.commit()
        except Exception as e:
            log.debug(e.message)
            session.rollback()
    
    return marsavin_page


def marsavin_pages_new(context, data_dict=None):
    '''Make a new page
    
    :param id: the id or name of the group to add the object to
    :type id: string
    
    :param title: the title of the page
    :type title: string
    
    :param name: the url safe name of the page
    :type name: string
    
    :param content: the id or name of the group to add the object to
    :type content: string
    
    :param lang: the id or name of the group to add the object to
    :type lang: string
    
    :param sidebar_content: the id or name of the group to add the object to
    :type sidebar_content: string
    
    :param order: the id or name of the group to add the object to
    :type order: string
    
    :param user_id: created user id of the page
    :type user_id: string

    :returns: the newly created (or updated) page
    :rtype: dictionary

    '''
    model = context['model']
    session = context['session']
    
    _check_access('ckanext_marsavin_pages_new', context, data_dict)
    
    context['schema'] = marsavin_pages_new_schema()
    
    return marsavin_pages_save(context, data_dict)


def marsavin_pages_edit(context, data_dict=None):
    '''Make a new page

    :param id: the id or name of the group to add the object to
    :type id: string

    :param title: the title of the page
    :type title: string

    :param name: the url safe name of the page
    :type name: string

    :param content: the id or name of the group to add the object to
    :type content: string

    :param lang: the id or name of the group to add the object to
    :type lang: string

    :param sidebar_content: the id or name of the group to add the object to
    :type sidebar_content: string

    :param order: the id or name of the group to add the object to
    :type order: string

    :param user_id: created user id of the page
    :type user_id: string

    :returns: the newly created (or updated) page
    :rtype: dictionary

    '''
    
    _check_access('ckanext_marsavin_pages_edit', context, data_dict)
    
    page_obj = MarsavinPages.by_page_lang(data_dict["name"], data_dict["lang"])
    if not page_obj:
        raise toolkit.ObjectNotFound
    
    data_dict["id"] = page_obj.id
    
    context["schema"] = marsavin_pages_edit_schema()

    return marsavin_pages_save(context, data_dict)


def marsavin_pages_list(context, data_dict):
    '''Return a list of the site's user accounts.

    :rtype: list of user dictionaries. User properties include:
      ``number_created_packages`` which excludes datasets which are private
      or draft state.

    '''
    lang = context['lang']

    _check_access('ckanext_marsavin_pages_list', context, data_dict)

    pages = MarsavinPages.by_lang(lang)
    
    pages_list = []
    for page in pages:
        page_dict = marsavin_pages_dictize(page, context)
        pages_list.append(page_dict)
    
    return pages_list


def marsavin_pages_show(context, data_dict={}):
    '''Return a list of the site's user accounts.

    :rtype: list of user dictionaries. User properties include:
      ``number_created_packages`` which excludes datasets which are private
      or draft state.

    '''
    page = _get_or_bust(data_dict, "name")
    lang = _get_or_bust(data_dict, "lang")
    
    _check_access('ckanext_marsavin_pages_read', context, data_dict)
    
    page_obj = MarsavinPages.by_page_lang(page, lang)
    
    if not page_obj:
        raise toolkit.ObjectNotFound
    
    return page_obj


def marsavin_pages_delete(context, data_dict):
    '''Delete a user.

    Only sysadmins can delete users.

    :param id: the id or usernamename of the user to delete
    :type id: string
    '''

    _check_access('ckanext_marsavin_pages_delete', context, data_dict)

    model = context['model']
    pages_name = _get_or_bust(data_dict, 'page')
    lang = _get_or_bust(data_dict, "lang")
    
    page = MarsavinPages.by_page_lang(pages_name, lang)

    if page is None:
        raise toolkit.ObjectNotFound('Page "{id}" was not found.'.format(
            id=pages_name))

    page.delete()

    model.repo.commit()
