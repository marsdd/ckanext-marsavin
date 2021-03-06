import ckan.lib.dictization as d
from ckan.logic import get_or_bust as _get_or_bust
from ckanext.marsavin.model.access_requests import AccessRequests
from ckanext.marsavin.model.package_marsavin import PackageMarsavin
from ckanext.marsavin.model.user_marsavin import UserMarsavin
from datetime import date
import logging

log = logging.getLogger(__name__)


# a.s.
def reqaccess_dict_save(reqaccess_dict, context):
    reqaccess = d.table_dict_save(reqaccess_dict, AccessRequests, context)

    return reqaccess


def package_marsavin_save(pkg_dict, context):
    package_id = _get_or_bust(pkg_dict, 'id')

    pkg_marsavin_dict = {
        "package_id": pkg_dict["id"],
        "associated_tasks": pkg_dict["associated_tasks"],
        "collection_period": pkg_dict["collection_period"],
        "geographical_area": pkg_dict["geographical_area"],
        "number_of_instances": pkg_dict["number_of_instances"],
        "pkg_description": pkg_dict["pkg_description"],
        "number_of_attributes": pkg_dict["number_of_attributes"],
        "has_missing_values": pkg_dict["has_missing_values"]
    }
    if pkg_dict["creation_date"]:
        pkg_marsavin_dict["creation_date"] = pkg_dict["creation_date"]
    if pkg_dict["expiry_date"]:
        pkg_marsavin_dict["expiry_date"] = pkg_dict["expiry_date"]

    entity = PackageMarsavin.by_package_id(package_id)

    if entity:
        pkg_marsavin_dict["id"] = entity.id

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


def package_marsavin_load(pkg_dict, cached_entity=None):
    package_id = _get_or_bust(pkg_dict, 'id')

    entity_dict = {
        "associated_tasks": u'',
        "collection_period": u'',
        "geographical_area": u'',
        "number_of_instances": u'',
        "pkg_description": u'',
        "number_of_attributes": u'',
        "creation_date": u'',
        "expiry_date": u'',
        "has_missing_values": u''
    }

    if isinstance(cached_entity, PackageMarsavin):
        entity = cached_entity
    else:
        entity = PackageMarsavin.by_package_id(package_id)

    if entity:
        entity_dict = {
            "associated_tasks": entity.associated_tasks,
            "collection_period": entity.collection_period,
            "geographical_area": entity.geographical_area,
            "number_of_instances": entity.number_of_instances,
            "pkg_description": entity.pkg_description,
            "number_of_attributes": entity.number_of_attributes,
            "has_missing_values": entity.has_missing_values,
            "creation_date": "",
            "expiry_date": ""
        }
        if entity.creation_date:
            if isinstance(entity.creation_date, date):
                entity_dict["creation_date"] = entity.creation_date.isoformat()
            else:
                entity_dict["creation_date"] = entity.creation_date

        if entity.expiry_date:
            if isinstance(entity.expiry_date, date):
                entity_dict["expiry_date"] = entity.expiry_date.isoformat()
            else:
                entity_dict["expiry_date"] = entity.expiry_date

    pkg_dict.update(entity_dict)


def user_marsavin_save(user_dict, context):
    user_id = _get_or_bust(user_dict, 'id')
    
    user_marsavin_dict = {
        "user_id": user_id,
    }
    try:
        user_marsavin_dict["allow_marketting_emails"] = user_dict[
            "allow_marketting_emails"]
    except KeyError:
        pass
    try:
        user_marsavin_dict["user-terms-agree"] = user_dict[
            "user-terms-agree"]
    except KeyError:
        pass
    try:
        user_marsavin_dict["uploader-terms-agree"] = user_dict[
            "uploader-terms-agree"]
    except KeyError:
        pass

    entity = UserMarsavin.by_user_id(user_id)

    if entity:
        user_marsavin_dict["id"] = entity.id

    user_marsavin = d.table_dict_save(user_marsavin_dict, UserMarsavin,
                                      context)
    return user_marsavin


def marsavin_pages_dictize(obj, context):
    pages_dict = {
        "title": obj.title,
        "name": obj.name,
        "content": obj.content,
        "lang": obj.lang,
        "sidebar_content": obj.sidebar_content,
        "order": obj.order,
        "created": obj.created,
        "modified": obj.modified,
    }
    return pages_dict
    
    