import ckan.lib.base as base
from ckan.lib.plugins import toolkit
from flask.views import MethodView
import ckan.model as model
import ckan.logic as logic
import ckan.lib.navl.dictization_functions as dict_fns
tuplize_dict = logic.tuplize_dict
clean_dict = logic.clean_dict
parse_params = logic.parse_params



def index():
    u''' display privacy page'''
    return base.render(u'pages/index.html', extra_vars={})


def edit(page):
    u''' display privacy page'''
    return base.render(u'pages/edit.html', extra_vars={})


def delete(page):
    u''' display privacy page'''
    return base.render(u'pages/delete.html', extra_vars={})


def read(page):
    u''' display privacy page'''
    return base.render(u'pages/read.html', extra_vars={})


class CreatePagesView(MethodView):
    u'''Create pages view '''
    def _prepare(self, data=None):
        context = {
            u'model': model,
            u'session': model.Session,
            u'user': toolkit.c.user,
            u'save': u'save' in toolkit.request.params,
        }

        try:
            toolkit.check_access(u'ckanext_marsavin_pages_new', context)
        except toolkit.NotAuthorized:
            base.abort(403, toolkit._(u'Unauthorized to create a group'))

        return context

    def post(self):
        context = self._prepare()

        try:
            data_dict = clean_dict(
                dict_fns.unflatten(tuplize_dict(parse_params(
                    toolkit.request.form))))
            
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

        return toolkit.redirect_to(u"marsavin_pages.index")

    def get(self, data=None, errors=None, error_summary=None):
        extra_vars = {
            "data": data or {},
            u'errors': errors,
            u'error_summary': error_summary,
            "attrs": {}
        }
        return base.render(u'pages/new.html', extra_vars=extra_vars)
        # set_org(is_organization)
        # context = self._prepare()
        # data = data or clean_dict(
        #     dict_fns.unflatten(
        #         tuplize_dict(
        #             parse_params(request.args, ignore_keys=CACHE_PARAMETERS)
        #         )
        #     )
        # )
        #
        # if not data.get(u'image_url', u'').startswith(u'http'):
        #     data.pop(u'image_url', None)
        # errors = errors or {}
        # error_summary = error_summary or {}
        # extra_vars = {
        #     u'data': data,
        #     u'errors': errors,
        #     u'error_summary': error_summary,
        #     u'action': u'new',
        #     u'group_type': group_type
        # }
        # _setup_template_variables(
        #     context, data, group_type=group_type)
        # form = base.render(
        #     _get_group_template(u'group_form', group_type), extra_vars)
        #
        # # TODO: Remove
        # # ckan 2.9: Adding variables that were removed from c object for
        # # compatibility with templates in existing extensions
        # g.form = form
        #
        # extra_vars["form"] = form
        # return base.render(
        #     _get_group_template(u'new_template', group_type), extra_vars)