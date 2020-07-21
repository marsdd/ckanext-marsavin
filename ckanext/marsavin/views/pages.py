import ckan.lib.base as base
from ckan.lib.plugins import toolkit


def index():
    u''' display privacy page'''
    return base.render(u'pages/index.html', extra_vars={})


def edit(page):
    u''' display privacy page'''
    return base.render(u'pages/edit.html', extra_vars={})


def delete(page):
    u''' display privacy page'''
    return base.render(u'pages/delete.html', extra_vars={})


def new():
    extra_vars = {
        "data": {},
        "errors": {},
        "attrs": {}
    }
    return base.render(u'pages/new.html', extra_vars=extra_vars)


def read(page):
    u''' display privacy page'''
    return base.render(u'pages/read.html', extra_vars={})
