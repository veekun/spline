import logging

from pylons import config, request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect_to
from routes import request_config
from sqlalchemy.orm.exc import NoResultFound

from spline import model
from spline.model import meta
from spline.lib import helpers as h
from spline.lib.base import BaseController, render

log = logging.getLogger(__name__)

class ForumController(BaseController):

    def forums(self):
        c.forums = meta.Session.query(model.Forum).order_by(model.Forum.id.asc())
        return render('/forum/forums.mako')

    def threads(self, forum_id):
        try:
            c.forum = meta.Session.query(model.Forum).get(forum_id)
        except NoResultFound:
            abort(404)

        return render('/forum/threads.mako')

    def posts(self, forum_id, thread_id):
        try:
            c.thread = meta.Session.query(model.Thread) \
                .filter_by(id=thread_id, forum_id=forum_id).one()
        except NoResultFound:
            abort(404)

        return render('/forum/threads.mako')
