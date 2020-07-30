from ckan.plugins import toolkit

def sysadmin(context, data_dict):
    return {'success':  False}


def anyone(context, data_dict):
    return {'success': True}

toolkit.auth_allow_anonymous_access(anyone)

pages_read = anyone
pages_edit = sysadmin
pages_new = sysadmin
pages_delete = sysadmin
pages_list = sysadmin
