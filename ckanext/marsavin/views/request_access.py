from ckan.logic.schema import reqaccess_new_form_schema
from flask.views import MethodView
from ckan import model, logic
from ckan.lib import base
from ckan.lib.navl import dictization_functions
from ckan.plugins import toolkit
from ckan.common import g, request


def _new_form_to_db_schema():
    return reqaccess_new_form_schema()


class RequestAccessView(MethodView):

    def _prepare(self):
        context = {
            u'model': model,
            u'session': model.Session,
            u'schema': _new_form_to_db_schema(),
            u'save': u'save' in request.form
        }

        return context

    def post(self):
        context = self._prepare()

        # a.s.
        data = request.form

        if 'save' in data:
            try:
                data_dict = logic.clean_dict(
                    dictization_functions.unflatten(
                        logic.tuplize_dict(logic.parse_params(request.form))))
            except dictization_functions.DataError:
                base.abort(400, toolkit._(u'Integrity Error'))

            context[u'message'] = data_dict.get(u'log_message', u'')

            try:
                logic.get_action(u'reqaccess_create')(context, data_dict)
            except logic.ValidationError as e:
                errors = e.error_dict
                error_summary = e.error_summary
                return self.get(data_dict, errors, error_summary)

            toolkit.h.flash_success(
                toolkit._(u'Request for dataset access has been sent. Data '
                          u'maintainer will respond to the following '
                          u'email: "%s" ') % (data_dict[u'user_email']))

            return base.render(u'home/index.html')

    def get(self, data=None, errors=None, error_summary=None):
        self._prepare()

        user_email = u'your_email@domain.com'
        if g.userobj and g.userobj.email:
            user_email = g.userobj.email
        maintainer_email = request.params.get('maintainer_email', u'')
        maintainer_name = request.params.get('maintainer_name', u'')
        resource_name = request.params.get('resource_name', u'')

        errors = errors or {}
        error_summary = error_summary or {}

        data = data or {
            'subject': u'AVIN Data Request',
            'maintainer_email': maintainer_email,
            'maintainer_name': maintainer_name,
            'resource_name': resource_name,
            'user_email': user_email,
            'user_msg': '',
            'title': u'Title',
        }

        form_vars = {
            u'data': data or {},
            u'errors': errors or {},
            u'error_summary': error_summary or {}
        }

        extra_vars = {
            u'form': base.render('mars/snippets/access_form_body.html',
                                 form_vars),
            u'data': data,
            u'errors': errors,
            u'error_summary': error_summary,
        }

        return base.render(u'mars/access_form.html', extra_vars)