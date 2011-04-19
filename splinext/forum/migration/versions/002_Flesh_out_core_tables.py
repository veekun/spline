from sqlalchemy import *
from sqlalchemy.sql.expression import text
from migrate import *
import migrate.changeset

from sqlalchemy.ext.declarative import declarative_base
TableBase = declarative_base()


class User(TableBase):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)

class Forum(TableBase):
    __tablename__ = 'forums'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    name = Column(Unicode(133), nullable=False)

class Thread(TableBase):
    __tablename__ = 'threads'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    forum_id = Column(Integer, ForeignKey('forums.id'), nullable=False)
    icon = Column(Unicode(32), nullable=True)
    subject = Column(Unicode(133), nullable=False)
    post_count = Column(Integer, nullable=False, server_default=text('0'))

thread_post_count_idx = Index('ix_threads_post_count', Thread.post_count)

class Post(TableBase):
    __tablename__ = 'posts'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    thread_id = Column(Integer, ForeignKey('threads.id'), nullable=False)
    position = Column(Integer, nullable=False, server_default=text('1'))
    author_user_id = Column(Integer, ForeignKey('users.id'), nullable=False, server_default=text('1'))
    posted_time = Column(DateTime, nullable=False, index=True)
    content = Column(Unicode(5120), nullable=False)

thread_position_idx = Index('thread_position', Post.thread_id, Post.position, unique=True)
posted_time_idx = Index('ix_posts_posted_time', Post.posted_time)


def upgrade(migrate_engine):
    TableBase.metadata.bind = migrate_engine

    Thread.__table__.c.icon.create()
    Thread.__table__.c.post_count.create()
    thread_post_count_idx.create(bind=migrate_engine)
    Post.__table__.c.position.create()
    Post.__table__.c.author_user_id.create()
    thread_position_idx.create(bind=migrate_engine)
    posted_time_idx.create(bind=migrate_engine)

def downgrade(migrate_engine):
    TableBase.metadata.bind = migrate_engine

    posted_time_idx.drop(bind=migrate_engine)
    thread_position_idx.drop(bind=migrate_engine)
    Post.__table__.c.author_user_id.drop()
    Post.__table__.c.position.drop()
    thread_post_count_idx.drop(bind=migrate_engine)
    Thread.__table__.c.post_count.drop()
    Thread.__table__.c.icon.drop()
