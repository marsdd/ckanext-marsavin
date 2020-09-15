import click
import logging
from ckan.lib.search.common import make_connection
from ckan import model
from ckanext.marsavin.model.package_marsavin import PackageMarsavin
import datetime
from ckan.lib.search import rebuild

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


@marsavin.command()
def delete_expired_packages():
    query = model.Session.query(model.Package, PackageMarsavin).filter(
        model.Package.id == PackageMarsavin.package_id
    ).filter(
        model.Package.state == "active"
    ).filter(
        PackageMarsavin.expiry_date < datetime.date.today()
    )
    
    expired_packages = query.all()
    
    if expired_packages:
        log.info("Found expired packages")
        for package in expired_packages:
            # model.package
            log.info("Deleting package {package_name} ({package_id}) "
                     "expired on {package_expired}".format(
                        package_name=package[0].name,
                        package_id=package[0].id,
                        package_expired=package[1].expiry_date))
            package[0].delete()
            rebuild(package[0].id)
    else:
        log.info("No expired packages found")
    
    model.repo.commit()
