import logging

from pylons import config, request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect
from routes import request_config
from sqlalchemy.orm.exc import NoResultFound
import wtforms
from wtforms import fields

from spline.model import meta
from spline.lib import helpers as h
from spline.lib.base import BaseController, render
import spline.lib.markdown
from splinext.forum import model as forum_model

log = logging.getLogger(__name__)


class WritePostForm(wtforms.Form):
    content = fields.TextAreaField('Content')

class WriteThreadForm(WritePostForm):
    subject = fields.TextField('Subject')

class ForumController(BaseController):

    def forums(self):
        c.forums = meta.Session.query(forum_model.Forum) \
            .order_by(forum_model.Forum.id.asc())
        return render('/forum/forums.mako')

    def threads(self, forum_id):
        c.forum = meta.Session.query(forum_model.Forum).get(forum_id)
        if not c.forum:
            abort(404)

        c.write_thread_form = WriteThreadForm()

        c.threads = c.forum.threads

        return render('/forum/threads.mako')

    def posts(self, forum_id, thread_id):
        try:
            c.thread = meta.Session.query(forum_model.Thread) \
                .filter_by(id=thread_id, forum_id=forum_id).one()
        except NoResultFound:
            abort(404)

        c.write_post_form = WritePostForm()

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
        post = forum_model.Post(
            position = 1,
            author_user_id = c.user.id,
            content = c.write_thread_form.content.data,
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
