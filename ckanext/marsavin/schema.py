from ckan.logic import schema as schema_
from ckan.logic.schema import validator_args, default_user_schema

# a.s.
# reqaccess schema
@validator_args
def default_reqaccess_schema(ignore_missing, unicode_safe, not_empty,
                             email_validator, ignore):
    return {
        'id': [ignore_missing, unicode_safe],
        'user_ip_address': [ignore_missing, unicode_safe],
        'user_email': [not_empty, unicode_safe, email_validator],
        'user_msg': [ignore_missing, unicode_safe],
        'maintainer_name': [not_empty, unicode_safe],
        'maintainer_email': [not_empty, unicode_safe, email_validator],
        'created': [ignore],
    }


@validator_args
def reqaccess_new_form_schema():
    schema = default_user_schema()

    return schema


# a.s. end of section
@validator_args
def default_update_user_schema(
        ignore_missing, name_validator, user_name_validator,
        unicode_safe, user_password_validator, boolean_validator):
    schema = schema_.default_user_schema()

    schema['name'] = [
        ignore_missing, name_validator, user_name_validator, unicode_safe]
    schema['password'] = [
        user_password_validator, ignore_missing, unicode_safe]
    
    schema['user-terms-agree'] = [boolean_validator, ]
    schema["allow_marketting_emails"] = [boolean_validator, ]
    
    return schema


@validator_args
def default_marsavin_pages_schema(
        ignore_missing, name_validator, int_validator, unicode_safe):
    
    schema = {
        "id": [
            ignore_missing,
            unicode_safe
        ],
        'title': [
            unicode_safe
        ],
        'name': [
            name_validator,
            unicode_safe
        ],
        'content': [
            unicode_safe,
            ignore_missing
        ],
        "lang": [
            unicode_safe
        ],
        "sidebar_content": [
            unicode_safe
        ],
        "order": [
            int_validator
        ],
        "created": [ignore_missing],
        "modified": [ignore_missing]
    }
    
    return schema
