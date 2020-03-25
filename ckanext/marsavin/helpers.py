import ckan.plugins.toolkit as toolkit
import ckan.lib.mailer as mailer
from ckan.common import config
from six import text_type
from cache import cacheable
from ckan import model
from hashlib import md5
from pprint import pprint
import requests
import logging

log = logging.getLogger(__name__)


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


def subscribe_to_mailchimp(userObj):
    audience_id = config.get("mailchimp_audience_id")
    api_key = config.get("mailchimp_api_key")
    root_url = "https://%s.api.mailchimp.com/3.0" % api_key.split("-")[1]
    user_md5 = md5(userObj.email.encode('utf-8')).hexdigest()
    
    # first check whether the user already exists or not
    user_retrieve_url = "%s/lists/%s/members/%s" \
                        % (root_url, audience_id, user_md5)
    user_res = requests.get(user_retrieve_url, auth=("MaRS", api_key))
    if user_res.status_code == requests.codes.ok:
        # we found the user but don't change subcription
        log.info("User with email %s already exists in mailchimp, "
                 "not changing status: \n %s" % (userObj.email, userObj))
        return
    
    user_add_request = {
        "email_address": userObj.email,
        "status": "subscribed",
        "tags": ["avindata"]
    }
    user_add_url = "%s/lists/%s/members" % (root_url, audience_id)
    user_add_res = requests.post(user_add_url, data=user_add_request)
    log.info("User add results: \n%s" % user_add_res)
    # following will raise an exception if the user failed
    user_add_res.raise_for_status()
    

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
    context = {
        u'model': model,
        u'session': model.Session,
        u'user': toolkit.c.user,
        u'for_view': True,
        u'with_private': False
    }
    data_dict = {
        "all_fields": True,
        "limit": kwargs.get("limit", 3),
        featured_list_key: featured_list,
        "sort": "name desc"
    }
    org_list = toolkit.get_action(action_name)(context, data_dict)
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


def render_resource_format(resource_formats):
    """
    Takes a csv and formats it to add the space
    :param resource_formats: the resource format string
    :type resource_formats: str
    :return: str
    """
    if u"," in resource_formats:
        return u", ".join(map(lambda x: x.strip(),
                              resource_formats.split(u",")))
    
    return resource_formats
