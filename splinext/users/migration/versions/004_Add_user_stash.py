from sqlalchemy import *
from migrate import *
import migrate.changeset  # monkeypatches Column

import json

from sqlalchemy import orm
from sqlalchemy.ext.declarative import declarative_base
TableBase = declarative_base()


class User(TableBase):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(length=20), nullable=False)
    unique_identifier = Column(Unicode(length=32), nullable=False)
    stash = Column(PickleType(pickler=json), nullable=True, default={})


def upgrade(migrate_engine):
    TableBase.metadata.bind = migrate_engine

    User.__table__.c.stash.create(table=User.__table__)
    User.__table__.c.stash.alter(nullable=False)

def downgrade(migrate_engine):
    TableBase.metadata.bind = migrate_engine

    User.__table__.c.stash.drop()
