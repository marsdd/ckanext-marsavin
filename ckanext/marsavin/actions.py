from helpers import _mail_recipient, get_package_resource_format_split
import ckan.logic as logic
import ckan
from ckanext.marsavin.dictization import reqaccess_dict_save
import logging
from ckan.plugins import toolkit
from ckanext.marsavin.schema import default_reqaccess_schema
import sqlalchemy
from sqlalchemy import text
import ckan.logic.schema as schema_
import ckan.lib.dictization.model_dictize as model_dictize
import ckan.lib.dictization.model_save as model_save

_func = sqlalchemy.func
_and_ = sqlalchemy.and_

# Define some shortcuts
# Ensure they are module-private so that they don't get loaded as available
# actions in the action API.
_validate = ckan.lib.navl.dictization_functions.validate
_check_access = logic.check_access
_get_action = logic.get_action
ValidationError = logic.ValidationError
NotFound = logic.NotFound
_get_or_bust = logic.get_or_bust

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


@schema_.validator_args
def default_update_user_schema(
        ignore_missing, name_validator, user_name_validator,
        unicode_safe, user_password_validator, boolean_validator):
    schema = schema_.default_user_schema()

    schema['name'] = [
        ignore_missing, name_validator, user_name_validator, unicode_safe]
    schema['password'] = [
        user_password_validator, ignore_missing, unicode_safe]
    
    schema['user-terms-agree'] = [boolean_validator, ]

    return schema


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

    user_obj = model.User.get(id)
    context['user_obj'] = user_obj
    if user_obj is None:
        raise NotFound('User was not found.')

    _check_access('user_update', context, data_dict)

    data, errors = _validate(data_dict, schema, context)
    if errors:
        session.rollback()
        raise ValidationError(errors)

    if user_obj.state == u'pending' and not data['user-terms-agree']:
        session.rollback()
        raise ValueError(toolkit._("You must agree to the Terms and "
                                   "Conditions"))

    # user schema prevents non-sysadmins from providing password_hash
    if 'password_hash' in data:
        data['_password'] = data.pop('password_hash')

    user = model_save.user_dict_save(data, context)

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