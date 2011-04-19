from sqlalchemy import *
from migrate import *

from sqlalchemy.ext.declarative import declarative_base
TableBase = declarative_base()

class Forum(TableBase):
    __tablename__ = 'forums'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    name = Column(Unicode(133), nullable=False)

class Thread(TableBase):
    __tablename__ = 'threads'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    forum_id = Column(Integer, ForeignKey('forums.id'), nullable=False)
    subject = Column(Unicode(133), nullable=False)

class Post(TableBase):
    __tablename__ = 'posts'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    thread_id = Column(Integer, ForeignKey('threads.id'), nullable=False)
    posted_time = Column(DateTime, nullable=False)
    content = Column(Unicode(5120), nullable=False)


def upgrade(migrate_engine):
    TableBase.bind = migrate_engine
    Forum.__table__.create()
    Thread.__table__.create()
    Post.__table__.create()

def downgrade(migrate_engine):
    TableBase.bind = migrate_engine
    Post.__table__.drop()
    Thread.__table__.drop()
    Forum.__table__.drop()
