from collections import namedtuple
import datetime

from sqlalchemy.orm import contains_eager, joinedload
from sqlalchemy.sql import func
from pylons import tmpl_context as c, url

from spline.model import meta

from splinext.forum import model as forum_model
from splinext.frontpage.sources import Source

FrontPageThread = namedtuple('FrontPageThread', ['source', 'time', 'post'])
class ForumSource(Source):
    """Represents a forum whose threads are put on the front page.

    ``link``, ``title``, and ``icon`` are all optional; the link and title
    default to the forum's thread list and name, and the icon defaults to a
    newspaper.

    Extra properties:

    ``forum_id``
        id of the forum to check for new threads.
    """

    template = '/forum/front_page.mako'

    def __init__(self, forum_id, **kwargs):
        forum = meta.Session.query(forum_model.Forum).get(forum_id)

        # Link is tricky.  Needs url(), which doesn't exist when this class is
        # loaded.  Lazy-load it in poll() below, instead
        kwargs.setdefault('link', None)
        kwargs.setdefault('title', forum.name)
        kwargs.setdefault('icon', 'newspapers')
        super(ForumSource, self).__init__(**kwargs)

        self.forum_id = forum_id

    def _poll(self, limit, max_age):
        if not self.link:
            self.link = url(
                controller='forum', action='threads', forum_id=self.forum_id)

        thread_q = meta.Session.query(forum_model.Thread) \
            .filter_by(forum_id=self.forum_id) \
            .join((forum_model.Post, forum_model.Thread.first_post)) \
            .options(
                contains_eager(forum_model.Thread.first_post, alias=forum_model.Post),
                contains_eager(forum_model.Thread.first_post, forum_model.Post.thread, alias=forum_model.Thread),
                joinedload(forum_model.Thread.first_post, forum_model.Post.author),
            )

        if max_age:
            thread_q = thread_q.filter(forum_model.Post.posted_time >= max_age)

        threads = thread_q \
            .order_by(forum_model.Post.posted_time.desc()) \
            [:limit]

        updates = []
        for thread in threads:
            update = FrontPageThread(
                source = self,
                time = thread.first_post.posted_time,
                post = thread.first_post,
            )
            updates.append(update)

        return updates

FrontPageActivity = namedtuple('FrontPageActivity', ['template', 'threads'])
def forum_activity(*args, **kwargs):
    """Show recently-active threads on the front page.

    Note that this isn't the most recent X threads; it's threads that are more
    recent than X, sorted by their activity since X.
    """
    # XXX this should be configurable probably
    cutoff = datetime.datetime.now() - datetime.timedelta(days=7)

    # TODO some sort of dropoff here idk
    active_threads_subq = meta.Session.query(
        forum_model.Post.thread_id.label('thread_id'),
        func.count('*').label('ranking'),
    ) \
        .filter(forum_model.Post.posted_time >= cutoff) \
        .group_by(forum_model.Post.thread_id) \
        .subquery()

    threads_q = meta.Session.query(forum_model.Thread) \
        .join((active_threads_subq,
            active_threads_subq.c.thread_id == forum_model.Thread.id)) \
        .order_by(active_threads_subq.c.ranking.desc()) \
        .limit(10)

    return FrontPageActivity(
        template='/forum/front_page_activity.mako',
        threads=threads_q.all(),
    )
