import ckan.plugins.toolkit as toolkit
import ckan.lib.mailer as mailer
from ckan.common import config
from six import text_type
from cache import cacheable
from ckan import model
from hashlib import md5
from mailchimp import mailchimp_get_member, get_merge_fields, update_member,\
    add_member, update_member_tags
from pprint import pprint
import requests
import logging
import os

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


def notify_mailchimp_subscribe_issue(email, error_message):
    recipient = {
        "display_name": os.environ['oce_email_distribution_group'],
        "email": os.environ['oce_email_distribution_group']
    }
    email_dict = {
        "subject": "Mailchimp subscription error",
        "body": u"""Error adding/updating mailchimp subscription for email: %s
        %s
        """ % (email, error_message)
    }
    toolkit.enqueue_job(_mail_recipient, [recipient, email_dict])


def subscribe_to_mailchimp(userObj):
    merge_field = get_merge_fields(filter_by_field_tag=["EXPCONSENT"])
    user_res = mailchimp_get_member(userObj.email)

    user_add_update = {
        "email_address": userObj.email,
        "status": "subscribed"
    }
    
    if user_res.status_code == requests.codes.ok:
        # pre-existing user
        user_res_obj = user_res.json()
        # does the merge field exist?
        if merge_field:
            try:
                if user_res_obj["merge_fields"]["EXPCONSENT"] != "I Consent":
                    user_add_update["merge_fields"] = {
                        "EXPCONSENT": "I Consent"
                    }
            except KeyError:
                user_add_update["merge_fields"] = {
                    "EXPCONSENT": "I Consent"
                }
        else:
            # if merge field doesn't exist send notification email
            notify_mailchimp_subscribe_issue(userObj.email,
                                             "Express consent field doesn't "
                                             "exist")

        user_update_res = update_member(userObj.email, user_add_update)
        # following will raise an exception if the user failed
        user_update_res.raise_for_status()
        
        # now take care of the tags if it's missing
        user_update_res_obj = user_update_res.json()
        new_tags = [{u"name": u"avindata", u"status": u"active"}]
        
        update_user_tags_res = update_member_tags(userObj.email, new_tags)
        # following will raise an exception if the user tags failed
        update_user_tags_res.raise_for_status()
        
        return

    # no pre-existing user, much simpler
    user_add_update["tags"] = ["avindata"]
    if merge_field:
        user_add_update["merge_fields"] = {
            "EXPCONSENT": "I Consent"
        }
    else:
        # if merge field doesn't exist send notification email
        notify_mailchimp_subscribe_issue(userObj.email,
                                         "Express consent field doesn't exist")

    user_add_res = add_member(user_add_update)
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
