from sqlalchemy import types, Column, Table, ForeignKey

from ckan.model import meta, domain_object, types as _types

__all__ = ['UserMarsavin', 'user_marsavin_table']

user_marsavin_table = Table('user_marsavin', meta.metadata,
    Column('id', types.UnicodeText, primary_key=True, default=_types.make_uuid),
    # NB: only (package, key) pair is unique
    Column('user_id', types.UnicodeText, ForeignKey('user.id')),
    Column('allow_marketting_emails', types.BOOLEAN),
    Column('user-terms-agree', types.BOOLEAN),
    Column('uploader-terms-agree', types.BOOLEAN)
)


class UserMarsavin(domain_object.DomainObject):
    @classmethod
    def by_user_id(cls, user_id, autoflush=True):
        obj = meta.Session.query(cls).autoflush(autoflush)\
              .filter_by(user_id=user_id).first()
        return obj


meta.mapper(UserMarsavin, user_marsavin_table)
