from sqlalchemy import types, Column, Table, func, UniqueConstraint

from ckan.model import meta, domain_object, types as _types
from datetime import datetime

__all__ = ['MarsavinPages', 'marsavin_pages_table']

marsavin_pages_table = Table('ckanext_marsavin_pages', meta.metadata,
                             Column('id', types.UnicodeText,
                                    default=_types.make_uuid,
                                    primary_key=True),
                             Column('title', types.UnicodeText),
                             Column('name', types.UnicodeText),
                             Column('content', types.UnicodeText),
                             Column('lang', types.UnicodeText),
                             Column('sidebar_content', types.UnicodeText),
                             Column('order', types.UnicodeText),
                             Column('created', types.TIMESTAMP,
                                    default=datetime.utcnow),
                             Column('modified', types.TIMESTAMP,
                                    onupdate=func.utcnow),
                             UniqueConstraint("name", "lang",
                                              name="u_name_lang")
                             )


class MarsavinPages(domain_object.DomainObject):
    @classmethod
    def by_page_lang(cls, page, lang, autoflush=True):
        obj = meta.Session.query(cls).autoflush(autoflush)\
              .filter_by(name=page, lang=lang).first()
        return obj


meta.mapper(MarsavinPages, marsavin_pages_table)
