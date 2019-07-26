import ckan.lib.dictization as d
from ckan.logic import get_or_bust as _get_or_bust, NotFound
from ckanext.marsavin.model.access_requests import AccessRequests
from ckanext.marsavin.model.package_marsavin import PackageMarsavin


# a.s.
def reqaccess_dict_save(reqaccess_dict, context):
    reqaccess = d.table_dict_save(reqaccess_dict, AccessRequests, context)

    return reqaccess


def package_marsavin_save(pkg_dict, context):

    pkg_marsavin_dict = {
        "package_id": pkg_dict["id"],
        "associated_tasks": pkg_dict["associated_tasks"],
        "collection_period": pkg_dict["collection_period"],
        "geographical_area": pkg_dict["geographical_area"],
        "number_of_instances": pkg_dict["number_of_instances"],
        "number_of_missing_values": pkg_dict["number_of_missing_values"],
        "pkg_description": pkg_dict["pkg_description"]
    }

    package_marsavin = d.table_dict_save(pkg_marsavin_dict, PackageMarsavin,
                                         context)
    return package_marsavin


def package_marsavin_delete(pkg_dict):
    package_id = _get_or_bust(pkg_dict, 'id')

    entity = PackageMarsavin.by_package_id(package_id)

    if entity:
        # object with package id may not be found, we don't really care since
        # it may only be found if the package exists
        entity.delete()


def package_marsavin_get(pkg_dict):
    package_id = _get_or_bust(pkg_dict, 'id')

    entity = PackageMarsavin.by_package_id(package_id)
    pkg_dict.update({
        "associated_tasks": entity["associated_tasks"],
        "collection_period": entity["collection_period"],
        "geographical_area": entity["geographical_area"],
        "number_of_instances": entity["number_of_instances"],
        "number_of_missing_values": entity["number_of_missing_values"],
        "pkg_description": entity["pkg_description"]
    })

    return pkg_dict