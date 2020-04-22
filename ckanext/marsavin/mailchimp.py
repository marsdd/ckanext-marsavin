from ckan.common import config
from hashlib import md5
import requests
import logging

log = logging.getLogger(__name__)


def mailchimp_get_auth():
    api_key = config.get("mailchimp_api_key")
    return "MaRS", api_key


def mailchimp_get_root_url():
    api_key = config.get("mailchimp_api_key")
    # api key format is ususally abcdABCD1234-us5 where us5 is the datacenter
    # for the mailchimp api where this key is valid
    return "https://%s.api.mailchimp.com/3.0" % api_key.split("-")[1]


def mailchimp_get(api_url, params=None):
    get_url = "%s%s" % (mailchimp_get_root_url(), api_url)
    res = requests.get(get_url, auth=mailchimp_get_auth(), params=params)
    return res


def mailchimp_put(api_url, data, params=None):
    put_url = "%s%s" % (mailchimp_get_root_url(), api_url)
    res = requests.put(put_url, data=data, auth=mailchimp_get_auth(),
                       params=params)
    return res


def mailchimp_get_member(user_email, audience_id=None):
    if not audience_id:
        audience_id = config.get("mailchimp_audience_id")
    user_md5 = md5(user_email.encode('utf-8')).hexdigest()
    # retrieve the user
    user_url = "/lists/%s/members/%s" % (audience_id, user_md5)
    
    return mailchimp_get(user_url)


def add_update_member(user_email, updated_values, audience_id=None):
    if not audience_id:
        audience_id = config.get("mailchimp_audience_id")
    user_md5 = md5(user_email.encode('utf-8')).hexdigest()
    user_update_url = "/lists/%s/members/%s" % (audience_id, user_md5)
    return mailchimp_put(api_url=user_update_url, data=updated_values)


def get_merge_fields(audience_id=None, field_type="radio",
                     filter_by_field_tag=None):
    if not audience_id:
        audience_id = config.get("mailchimp_audience_id")
    
    params = {
        "limit": 100
    }
    if field_type:
        params["type"] = field_type
    
    # retrieve the merge fields
    merge_field_url = "/lists/%s/merge_fields" % audience_id
    
    merge_fields_res = mailchimp_get(merge_field_url, params).json()
    
    # if no data filtering is necessary, we are done, return the results
    if not filter_by_field_tag:
        return merge_fields_res["merge_fields"]
    
    merge_fields_res = filter(lambda res_merge_field: res_merge_field.tag in
                                                      filter_by_field_tag,
                              merge_fields_res["merge_fields"])
    
    return merge_fields_res
