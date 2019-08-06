import ckan.lib.base as base


def contact():
    u''' display contact page'''
    return base.render(u'home/contact.html', extra_vars={})


def terms():
    u''' display terms page'''
    return base.render(u'home/terms_conditions.html', extra_vars={})


def privacy():
    u''' display privacy page'''
    return base.render(u'home/privacy.html', extra_vars={})
