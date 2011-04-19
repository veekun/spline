from sqlalchemy import *
from migrate import *
import migrate.changeset

from sqlalchemy.ext.declarative import declarative_base
TableBase = declarative_base()

class Forum(TableBase):
    __tablename__ = 'forums'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    name = Column(Unicode(133), nullable=False)
    description = Column(Unicode(1024), nullable=False, default=u'', server_default=u'')
    access_level = Column(Enum(u'normal', u'soapbox', u'archive', name='forums_access_level'), nullable=False, default=u'normal', server_default=u'normal')


def upgrade(migrate_engine):
    TableBase.metadata.bind = migrate_engine

    # populate_default gets all retarded I don't even
    Forum.__table__.c.description.create(populate_default=False)

def downgrade(migrate_engine):
    TableBase.metadata.bind = migrate_engine

    Forum.__table__.c.description.drop()
