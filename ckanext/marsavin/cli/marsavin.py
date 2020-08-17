import click
import logging
from ckan.lib.search.common import make_connection

log = logging.getLogger(__name__)


@click.group(name=u"marsavin", short_help=u"Mars Avin module commands")
def marsavin():
    pass


@marsavin.command()
def update_package_search_schema():
    fields = {
        "associated_tasks": b'{"add-field":{"name": '
                            b'"associated_tasks",  "type": "textgen", '
                            b'"indexed": "true", stored: "true"}}',
        "collection_period": b'{"add-field":{"name": '
                             b'"collection_period",  "type": "textgen", '
                             b'"indexed": "true", stored: "true"}}',
        "geographical_area": b'{"add-field":{"name": '
                             b'"geographical_area",  "type": "textgen", '
                             b'"indexed": "true", stored: "true"}}',
        "number_of_instances": b'{"add-field":{"name": '
                               b'"number_of_instances",  '
                               b'"type": "textgen", '
                               b'"indexed": "true", stored: "true"}}',
        "number_of_attributes": b'{"add-field":{"name": '
                                b'"number_of_attributes",  '
                                b'"type": "textgen", '
                                b'"indexed": "true", stored: "true"}}',
        "pkg_description": b'{"add-field":{"name": '
                           b'"pkg_description",  "type": "textgen", '
                           b'"indexed": "true", stored: "true"}}',
        "creation_date": b'{"add-field":{"name": '
                         b'"creation_date",  "type": "date", '
                         b'"indexed": "true", stored: "true"}}',
        "expiry_date": b'{"add-field":{"name": '
                       b'"expiry_date",  "type": "date", '
                       b'"indexed": "true", stored: "true"}}',
        "has_missing_values": b'{"add-field":{"name": '
                              b'"has_missing_values",  '
                              b'"type": "boolean", '
                              b'"indexed": "true", stored: "true"}}',
    }
    
    copy_fields = {
        "associated_tasks": b'{"add-copy-field":{"source": '
                            b'"associated_tasks",  "dest": "text"}}',
        "collection_period": b'{"add-copy-field":{"source": '
                             b'"collection_period",  "dest": "text"}}',
        "geographical_area": b'{"add-copy-field":{"source": '
                             b'"geographical_area",  "dest": "text"}}',
        "pkg_description": b'{"add-copy-field":{"source": '
                           b'"pkg_description",  "dest": "text"}}'
    }
    
    conn = make_connection()
    path = "schema"
    for fieldname in fields:
        res = conn._send_request("post", path, fields[fieldname])
        log.debug("Result of update {result}".format(result=res))
    
    for fieldname in copy_fields:
        res = conn._send_request("post", path, copy_fields[fieldname])
        log.debug("Result of update {result}".format(result=res))
    pass
