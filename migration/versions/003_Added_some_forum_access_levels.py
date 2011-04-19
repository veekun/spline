from sqlalchemy import *
from migrate import *
import migrate.changeset

from sqlalchemy.ext.declarative import declarative_base
TableBase = declarative_base()


class Forum(TableBase):
    __tablename__ = 'forums'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    name = Column(Unicode(133), nullable=False)
    access_level = Column(Enum(u'normal', u'soapbox', u'archive', name='forums_access_level'), nullable=False, server_default=u'normal')


def upgrade(migrate_engine):
    TableBase.metadata.bind = migrate_engine

    Forum.__table__.c.access_level.type.create(bind=migrate_engine)
    Forum.__table__.c.access_level.create()

def downgrade(migrate_engine):
    TableBase.metadata.bind = migrate_engine
    access_level_type = Forum.__table__.c.access_level.type

    Forum.__table__.c.access_level.drop()
    access_level_type.drop(bind=migrate_engine)
