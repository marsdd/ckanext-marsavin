from helpers import _mail_recipient
import ckan.logic as logic
import ckan
import ckan.lib.dictization.model_save as model_save
import logging
from ckan.plugins import toolkit

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
    # schema = context.get('schema') or ckan.logic.schema.default_reqaccess_schema()
    schema = ckan.logic.schema.default_reqaccess_schema()
    session = context['session']

    data, errors = _validate(data_dict, schema, context)

    if errors:
        for er in errors:
            log.info(
                'Validation errors in create.py a.s. - {er}'.format(er=er))

        session.rollback()
        raise ValidationError(errors)

    model_save.reqaccess_dict_save(data, context)

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