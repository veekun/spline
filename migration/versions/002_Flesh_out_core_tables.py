from sqlalchemy import *
from sqlalchemy.sql.expression import text
from migrate import *
import migrate.changeset

from sqlalchemy.ext.declarative import declarative_base
TableBase = declarative_base(bind=migrate_engine)


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


objects = [
    Thread.__table__.c.icon,
    Thread.__table__.c.post_count,
    thread_post_count_idx,
    Post.__table__.c.position,
    Post.__table__.c.author_user_id,
    thread_position_idx,
    posted_time_idx,
]

def upgrade():
    for obj in objects:
        obj.create()

def downgrade():
    for obj in reversed(objects):
        obj.drop()
