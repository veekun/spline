import logging

from pylons import config, request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect_to
from routes import request_config
from sqlalchemy.orm.exc import NoResultFound

from spline.model import meta
from spline.lib import helpers as h
from spline.lib.base import BaseController, render
from splinext.forum import model as forum_model

log = logging.getLogger(__name__)

class ForumController(BaseController):

    def forums(self):
        c.forums = meta.Session.query(forum_model.Forum) \
            .order_by(forum_model.Forum.id.asc())
        return render('/forum/forums.mako')

    def threads(self, forum_id):
        try:
            c.forum = meta.Session.query(forum_model.Forum).get(forum_id)
        except NoResultFound:
            abort(404)

        return render('/forum/threads.mako')

    def posts(self, forum_id, thread_id):
        try:
            c.thread = meta.Session.query(forum_model.Thread) \
                .filter_by(id=thread_id, forum_id=forum_id).one()
        except NoResultFound:
            abort(404)

        return render('/forum/threads.mako')
