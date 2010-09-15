import datetime
import logging
import math

from pylons import cache, config, request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect
from routes import request_config
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql import func
import wtforms
from wtforms import fields

from spline.model import meta
from spline.lib import helpers as h
from spline.lib.base import BaseController, render
import spline.lib.markdown
from splinext.forum import model as forum_model

log = logging.getLogger(__name__)


def forum_activity_score(forum):
    """Returns a number representing how active a forum is, based on the past
    week.

    The calculation is arbitrary, but 0 is supposed to mean "dead" and 1 is
    supposed to mean "healthy".
    """
    cutoff = datetime.datetime.now() - datetime.timedelta(days=7)

    post_count = meta.Session.query(forum_model.Post) \
        .join(forum_model.Post.thread) \
        .filter(forum_model.Thread.forum == forum) \
        .filter(forum_model.Post.posted_time >= cutoff) \
        .count()

    # Avoid domain errors!
    if not post_count:
        return 0.0

    # The log is to scale 0 posts to 0.0, and 168 posts to 1.0.
    # The square is really just to take the edge off the log curve; it
    # accelerates to 1 very quickly, then slows considerably after that.
    # Squaring helps both of these problems.
    score = (math.log(post_count) / math.log(168)) ** 2

    # TODO more threads and more new threads should boost the score slightly

    return score

def get_forum_activity():
    """Returns a hash mapping forum ids to their level of 'activity'."""
    forums_q = meta.Session.query(forum_model.Forum)

    activity = {}
    for forum in forums_q:
        activity[forum.id] = forum_activity_score(forum)

    return activity

def get_forum_volume():
    """Returns a hash mapping forum ids to the percentage of all posts that
    reside in that forum.
    """
    # Do a complicated-ass subquery to get a list of forums and postcounts
    volume_q = meta.Session.query(
            forum_model.Forum.id.label('forum_id'),
            func.count(forum_model.Post.id).label('post_count'),
        ) \
        .outerjoin(forum_model.Thread) \
        .outerjoin(forum_model.Post) \
        .group_by(forum_model.Forum.id)

    # Stick this into a hash, and count the number of total posts
    total_posts = 0
    volume = {}
    for forum_id, post_count in volume_q:
        post_count = float(post_count or 0)
        volume[forum_id] = post_count
        total_posts += post_count

    # Divide, to get a percentage
    if total_posts:
        for forum_id, post_count in volume.iteritems():
            volume[forum_id] /= total_posts

    return volume


class WritePostForm(wtforms.Form):
    content = fields.TextAreaField('Content')

class WriteThreadForm(WritePostForm):
    subject = fields.TextField('Subject')

class ForumController(BaseController):

    def forums(self):
        c.forums = meta.Session.query(forum_model.Forum) \
            .order_by(forum_model.Forum.id.asc()) \
            .all()

        # Get some forum stats.  Cache them because they're a bit expensive to
        # compute.  Expire after an hour.
        # XXX when there are admin controls, they'll need to nuke this cache
        # when messing with the forum list
        forum_cache = cache.get_cache('spline-forum', expiretime=3600)
        c.forum_activity = forum_cache.get_value(
            key='forum_activity', createfunc=get_forum_activity)
        c.forum_volume = forum_cache.get_value(
            key='forum_volume', createfunc=get_forum_volume)

        c.max_volume = max(c.forum_volume.itervalues()) or 1

        # Need to know the last post for each forum, in realtime
        c.last_post = {}
        last_post_subq = meta.Session.query(
                forum_model.Forum.id.label('forum_id'),
                func.max(forum_model.Post.posted_time).label('posted_time'),
            ) \
            .outerjoin(forum_model.Thread) \
            .outerjoin(forum_model.Post) \
            .group_by(forum_model.Forum.id) \
            .subquery()
        last_post_q = meta.Session.query(
                forum_model.Post,
                last_post_subq.c.forum_id,
            ) \
            .join((
                last_post_subq,
                forum_model.Post.posted_time == last_post_subq.c.posted_time,
            )) \
            .options(
                joinedload('thread'),
                joinedload('author'),
            )
        for post, forum_id in last_post_q:
            c.last_post[forum_id] = post

        return render('/forum/forums.mako')

    def threads(self, forum_id):
        c.forum = meta.Session.query(forum_model.Forum).get(forum_id)
        if not c.forum:
            abort(404)

        c.write_thread_form = WriteThreadForm()

        # nb: This will never show post-less threads.  Oh well!
        threads_q = c.forum.threads \
            .join(forum_model.Thread.last_post) \
            .order_by(forum_model.Post.posted_time.desc()) \
            .options(joinedload('last_post.author'))
        c.num_threads = threads_q.count()
        try:
            c.skip = int(request.params.get('skip', 0))
        except ValueError:
            abort(404)
        c.per_page = 89
        c.threads = threads_q.offset(c.skip).limit(c.per_page)

        return render('/forum/threads.mako')

    def posts(self, forum_id, thread_id):
        try:
            c.thread = meta.Session.query(forum_model.Thread) \
                .filter_by(id=thread_id, forum_id=forum_id).one()
        except NoResultFound:
            abort(404)

        c.write_post_form = WritePostForm()

        posts_q = c.thread.posts \
            .order_by(forum_model.Post.position.asc()) \
            .options(joinedload('author'))
        c.num_posts = c.thread.post_count
        try:
            c.skip = int(request.params.get('skip', 0))
        except ValueError:
            abort(404)
        c.per_page = 89
        c.posts = posts_q.offset(c.skip).limit(c.per_page)

        return render('/forum/posts.mako')


    def write_thread(self, forum_id):
        """Provides a form for posting a new thread."""
        if not c.user.can('forum:create-thread'):
            abort(403)

        try:
            c.forum = meta.Session.query(forum_model.Forum) \
                .filter_by(id=forum_id).one()
        except NoResultFound:
            abort(404)

        c.write_thread_form = WriteThreadForm(request.params)

        if request.method != 'POST' or not c.write_thread_form.validate():
            # Failure or initial request; show the form
            return render('/forum/write_thread.mako')


        # Otherwise, add the post.
        c.forum = meta.Session.query(forum_model.Forum) \
            .with_lockmode('update') \
            .get(c.forum.id)

        thread = forum_model.Thread(
            forum_id = c.forum.id,
            subject = c.write_thread_form.subject.data,
            post_count = 1,
        )
        source = c.write_thread_form.content.data
        post = forum_model.Post(
            position = 1,
            author_user_id = c.user.id,
            raw_content = source,
            content = spline.lib.markdown.translate(source),
        )

        thread.posts.append(post)
        c.forum.threads.append(thread)

        meta.Session.commit()

        # Redirect to the new thread
        h.flash("Contribution to the collective knowledge of the species successfully recorded.")
        redirect(
            url(controller='forum', action='posts',
                forum_id=forum_id, thread_id=thread.id),
            code=303,
        )

    def write(self, forum_id, thread_id):
        """Provides a form for posting to a thread."""
        if not c.user.can('forum:create-post'):
            abort(403)

        try:
            c.thread = meta.Session.query(forum_model.Thread) \
                .filter_by(id=thread_id, forum_id=forum_id).one()
        except NoResultFound:
            abort(404)

        c.write_post_form = WritePostForm(request.params)

        if request.method != 'POST' or not c.write_post_form.validate():
            # Failure or initial request; show the form
            return render('/forum/write.mako')


        # Otherwise, add the post.
        c.thread = meta.Session.query(forum_model.Thread) \
            .with_lockmode('update') \
            .get(c.thread.id)

        source = c.write_post_form.content.data
        post = forum_model.Post(
            position = c.thread.post_count + 1,
            author_user_id = c.user.id,
            raw_content = source,
            content = spline.lib.markdown.translate(source),
        )

        c.thread.posts.append(post)
        c.thread.post_count += 1

        meta.Session.commit()

        # Redirect to the thread
        # XXX probably to the post instead; anchor?  depends on paging scheme
        h.flash('Your uniqueness has been added to our own.')
        redirect(
            url(controller='forum', action='posts',
                forum_id=forum_id, thread_id=thread_id),
            code=303,
        )
