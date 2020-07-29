import ckan.lib.base as base
from ckan.lib.i18n import get_lang
from ckan.lib.plugins import toolkit
from flask.views import MethodView
import ckan.model as model
import ckan.logic as logic
import ckan.lib.navl.dictization_functions as dict_fns
tuplize_dict = logic.tuplize_dict
clean_dict = logic.clean_dict
parse_params = logic.parse_params


def load_page(page):
    lang = get_lang()
    data_dict = {
        u"name": page,
        u"lang": lang
    }
    context = {
        u"model": model,
        u"session": model.Session
    }
    
    return logic.get_action(u'marsavin_pages_show')(context, data_dict)


def index():
    context = {
        u'model': model,
        u'session': model.Session,
        u'lang': get_lang()
    }
    data_dict = {}
    pages = logic.get_action(u'marsavin_pages_list')(context, data_dict)
    extra_vars = {
        u'pages': pages
    }
    u''' display privacy page'''
    return base.render(u'pages/index.html', extra_vars=extra_vars)


def delete(page):
    u'''Delete user with id passed as parameter'''
    context = {
        u'model': model,
        u'session': model.Session
    }
    data_dict = {
        u'page': page,
        u'lang': get_lang()
    }
    
    try:
        logic.get_action(u'marsavin_pages_delete')(context, data_dict)
    except logic.NotAuthorized:
        msg = toolkit._(u'Unauthorized to delete user with id "{user_id}".')
        base.abort(403, msg.format(user_id=id))

    return toolkit.redirect_to(toolkit.url_for(u'marsavin_pages.index'))


def read(page):
    try:
        page_obj = load_page(page)
    except toolkit.ObjectNotFound:
        base.abort(404)
        
    extra_vars = {
        u"page": page_obj
    }
    u''' display privacy page'''
    return base.render(u'pages/read.html', extra_vars=extra_vars)


class EditPagesView(MethodView):
    u'''Create pages view '''
    
    def _prepare(self, page):
        context = {
            u'model': model,
            u'session': model.Session,
            u'user': toolkit.c.user,
            u'save': u'save' in toolkit.request.params,
        }
        
        if not page:
            base.abort(400, toolkit._(u'Invalid page specified'))
        
        try:
            toolkit.check_access(u'ckanext_marsavin_pages_edit', context)
        except toolkit.NotAuthorized:
            base.abort(403, toolkit._(u'Unauthorized to edit a page'))
        
        return context
    
    def post(self, page):
        context = self._prepare(page)
        try:
            data_dict = clean_dict(
                dict_fns.unflatten(tuplize_dict(parse_params(
                    toolkit.request.form))))
            
            data_dict[u"lang"] = get_lang()
            page = toolkit.get_action(u"marsavin_pages_edit")(context,
                                                              data_dict)
        except (toolkit.ObjectNotFound) as e:
            base.abort(404, toolkit._(u'Page not found: %s' % e))
        except dict_fns.DataError:
            base.abort(400, toolkit._(u'Integrity Error'))
        except toolkit.ValidationError as e:
            errors = e.error_dict
            error_summary = e.error_summary
            return self.get(data_dict, errors, error_summary)
        
        return toolkit.redirect_to(u"marsavin_pages.read", page=page.name)
    
    def get(self, page=None, data=None, errors=None, error_summary=None):
        try:
            page_obj = load_page(page)
        except toolkit.ObjectNotFound:
            base.abort(404, u"That page is not found")
            
        extra_vars = {
            "data": page_obj,
            u'errors': errors,
            u'error_summary': error_summary,
            "attrs": {}
        }
        return base.render(u'pages/edit.html', extra_vars=extra_vars)


class CreatePagesView(MethodView):
    u'''Create pages view '''
    def _prepare(self, data=None):
        context = {
            u'model': model,
            u'session': model.Session,
            u'user': toolkit.c.user,
            u'save': u'save' in toolkit.request.params
        }

        try:
            toolkit.check_access(u'ckanext_marsavin_pages_new', context)
        except toolkit.NotAuthorized:
            base.abort(403, toolkit._(u'Unauthorized to create a page'))

        return context

    def post(self):
        context = self._prepare()
        try:
            data_dict = clean_dict(
                dict_fns.unflatten(tuplize_dict(parse_params(
                    toolkit.request.form))))
            
            data_dict[u"lang"] = get_lang()
            
            page = toolkit.get_action(u"marsavin_pages_new")(context,
                                                             data_dict)
        except (toolkit.ObjectNotFound) as e:
            base.abort(404, toolkit._(u'Page not found: %s' % e))
        except dict_fns.DataError:
            base.abort(400, toolkit._(u'Integrity Error'))
        except toolkit.ValidationError as e:
            errors = e.error_dict
            error_summary = e.error_summary
            return self.get(data_dict, errors, error_summary)

        return toolkit.redirect_to(u"marsavin_pages.read", page=page.name)

    def get(self, data=None, errors=None, error_summary=None):
        extra_vars = {
            "data": data or {},
            u'errors': errors,
            u'error_summary': error_summary,
            "attrs": {}
        }
        return base.render(u'pages/new.html', extra_vars=extra_vars)
