from sqlalchemy import types, Column, Table, ForeignKey

from ckan.model import meta, domain_object, types as _types

__all__ = ['PackageMarsavin', 'package_marsavin_table']

package_marsavin_table = Table('package_marsavin', meta.metadata,
    Column('id', types.UnicodeText, primary_key=True, default=_types.make_uuid),
    # NB: only (package, key) pair is unique
    Column('package_id', types.UnicodeText, ForeignKey('package.id')),
    Column('associated_tasks', types.UnicodeText),
    Column('collection_period', types.UnicodeText),
    Column('geographical_area', types.UnicodeText),
    Column('number_of_instances', types.UnicodeText),
    Column('pkg_description', types.UnicodeText),
    Column('number_of_attributes', types.UnicodeText),
    Column('creation_date', types.DateTime),
    Column('expiry_date', types.DateTime),
    Column('has_missing_values', types.Boolean)
)


class PackageMarsavin(domain_object.DomainObject):

    @classmethod
    def by_package_id(cls, package_id, autoflush=True):
        obj = meta.Session.query(cls).autoflush(autoflush)\
              .filter_by(package_id=package_id).first()
        return obj

    @classmethod
    def get_test(data=None):
        return


meta.mapper(PackageMarsavin, package_marsavin_table)
