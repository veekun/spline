from datetime import datetime

from sqlalchemy import and_, Column, ForeignKey, Index
from sqlalchemy.orm import relation
from sqlalchemy.types import DateTime, Enum, Integer, Unicode

from spline.model.meta import TableBase
from splinext.users import model as users_model


### Core

class Forum(TableBase):
    __tablename__ = 'forums'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    name = Column(Unicode(133), nullable=False)
    description = Column(Unicode(1024), nullable=False, default=u'', server_default=u'')
    access_level = Column(Enum(u'normal', u'soapbox', u'archive', name='forums_access_level'), nullable=False, default=u'normal', server_default=u'normal')

    def can_create_thread(self, user):
        """Returns True ifff the named user can make a new thread in this
        forum.
        """
        if not user.can('forum:create-thread'):
            return False

        if self.access_level == u'soapbox' and \
            not user.can('forum:override-soapbox'):
            return False

        if self.access_level == u'archive' and \
            not user.can('forum:override-archive'):
            return False

        return True

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

    def can_create_post(self, user):
        """Returns True ifff the named user can make a new post in this thread.
        """
        if not user.can('forum:create-post'):
            return False

        if self.forum.access_level == u'archive' and \
            not user.can('forum:override-archive'):
            return False

        return True

class Post(TableBase):
    __tablename__ = 'posts'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    thread_id = Column(Integer, ForeignKey('threads.id'), nullable=False)
    position = Column(Integer, nullable=False)
    author_user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    posted_time = Column(DateTime, nullable=False, index=True, default=datetime.now)
    raw_content = Column(Unicode(5120), nullable=False)
    content = Column(Unicode(5120), nullable=False)

Index('thread_position', Post.thread_id, Post.position, unique=True)


# XXX sort by time, how?
Forum.threads = relation(Thread, order_by=Thread.id.desc(), lazy='dynamic', backref='forum')

Thread.posts = relation(Post, order_by=Post.position.asc(), lazy='dynamic', backref='thread')
Thread.first_post = relation(Post, primaryjoin=and_(Post.thread_id == Thread.id, Post.position == 1), uselist=False)
# XXX THIS WILL NEED TO CHANGE when posts can be deleted!  Or change what 'position' means
Thread.last_post = relation(Post, primaryjoin=and_(Post.thread_id == Thread.id, Post.position == Thread.post_count), uselist=False)

Post.author = relation(users_model.User, backref='posts')
