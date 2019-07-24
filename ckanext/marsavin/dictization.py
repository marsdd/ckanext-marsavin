import ckan.lib.dictization as d
from ckanext.marsavin.model.access_requests import AccessRequests


# a.s.
def reqaccess_dict_save(reqaccess_dict, context):
    model = context['model']
    session = context['session']
    reqaccess = d.table_dict_save(reqaccess_dict, AccessRequests, context)

    return reqaccess