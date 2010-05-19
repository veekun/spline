from datetime import datetime

from sqlalchemy import and_, Column, ForeignKey, Index
from sqlalchemy.orm import relation
from sqlalchemy.types import DateTime, Integer, Unicode

from spline.model.meta import TableBase
from splinext.users import model as users_model


### Core

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
    post_count = Column(Integer, nullable=False, default=0, index=True)

    def specific_post(self, position):
        """Returns post number `position` in this thread.

        Positions are one-indexed.  Negative indexes are allowed.
        """

        # Handle negative indexes
        if position < 0:
            position = self.post_count + position + 1

        return self.posts.filter_by(position=position).one()

class Post(TableBase):
    __tablename__ = 'posts'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    thread_id = Column(Integer, ForeignKey('threads.id'), nullable=False)
    position = Column(Integer, nullable=False)
    author_user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    posted_time = Column(DateTime, nullable=False, index=True, default=datetime.now)
    content = Column(Unicode(5120), nullable=False)

Index('thread_position', Post.thread_id, Post.position, unique=True)


# XXX sort by time, how?
Forum.threads = relation(Thread, order_by=Thread.id.desc(), lazy='dynamic', backref='forum')

Thread.posts = relation(Post, order_by=Post.posted_time.desc(), lazy='dynamic', backref='thread')
Thread.first_post = relation(Post, primaryjoin=and_(Post.thread_id == Thread.id, Post.position == 1), uselist=False)
Thread.last_post = relation(Post, primaryjoin=and_(Post.thread_id == Thread.id, Post.position == Thread.post_count), uselist=False)

Post.author = relation(users_model.User, backref='posts')
