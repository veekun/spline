from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relation
from sqlalchemy.types import DateTime, Integer, Unicode

from spline.model.meta import TableBase

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


# XXX sort by time, how?
Forum.threads = relation(Thread, order_by=Thread.id.desc(), backref='forum')

Thread.posts = relation(Post, order_by=Post.posted_time.desc(), backref='thread')
