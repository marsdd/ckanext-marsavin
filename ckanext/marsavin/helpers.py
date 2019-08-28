import ckan.plugins.toolkit as toolkit
import ckan.lib.mailer as mailer
from ckan.common import config
from six import text_type
from cache import cacheable


def _mail_recipient(recipient=None, email_dict=None):
    try:
        # send email
        email = {'recipient_name': recipient['display_name'],
                 'recipient_email': recipient['email'],
                 'subject': email_dict['subject'],
                 'body': email_dict['body'],
                 #  'headers': {'header1': 'value1'}
                 }
        mailer.mail_recipient(**email)

    except mailer.MailerException as e:
        toolkit.h.flash_error(toolkit._('Could not send an email: %s') %
                              text_type(e))
        raise
    return


def is_featured_organization(name):
    featured_orgs = config.get('ckan.featured_orgs', '').split()
    return name in featured_orgs


@cacheable
def get_homepage_featured_organizations():
    featured_orgs = config.get('ckan.featured_orgs_homepage', '').split()
    org_list = toolkit.get_action("organization_list")({}, {
        "all_fields": True,
        "limit": 3,
        "organizations": featured_orgs,
        "sort": "name desc"
    })
    return org_list