def sysadmin(context, data_dict):
    return {'success':  False}


def anyone(context, data_dict):
    return {'success': True}


pages_read = anyone
pages_edit = sysadmin
pages_new = sysadmin
pages_delete = sysadmin
pages_list = sysadmin
