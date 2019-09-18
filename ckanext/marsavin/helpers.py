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
    featured_list = config.get('ckan.featured_orgs_homepage', '').split()
    return _get_homepage_featured_orgs_groups("organization_list",
                                              featured_list)


@cacheable
def get_homepage_featured_groups():
    featured_list = config.get('ckan.featured_groups_homepage', '').split()
    return _get_homepage_featured_orgs_groups("group_list", featured_list,
                                              limit=6)


def _get_homepage_featured_orgs_groups(action_name, featured_list, **kwargs):
    featured_list_key = "groups" if action_name == "group_list" else "organizations"
    org_list = toolkit.get_action(action_name)({}, {
        "all_fields": True,
        "limit": kwargs.get("limit", 3),
        featured_list_key: featured_list,
        "sort": "name desc"
    })
    return org_list


def get_package_resource_format_split(resource_formats):
    updated_res_formats = []
    if isinstance(resource_formats, list):
        for format in resource_formats:
            if u"," in format:
                updated_res_formats.extend(format.split(u","))
            else:
                updated_res_formats.append(format)
    if updated_res_formats:
        updated_res_formats = list(set(updated_res_formats))
    return updated_res_formats


def get_resource_data_format(resource_formats):
    if u"," in resource_formats:
        return resource_formats.split(u",")
    return resource_formats