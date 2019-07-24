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
