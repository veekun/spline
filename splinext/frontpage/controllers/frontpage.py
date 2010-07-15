import logging

from pylons import config, request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect_to
from routes import request_config
from sqlalchemy.orm.exc import NoResultFound

from spline.lib import helpers as h
from spline.lib.base import BaseController, render
from spline.lib.plugin.load import run_hooks

log = logging.getLogger(__name__)

class FrontPageController(BaseController):

    def index(self):
        """Magicaltastic front page.

        Plugins can register things to appear on it, somehow.

        Local plugins can override the fairly simple index.mako template to
        customize the front page layout.
        """
        # Hooks should return a list of FrontPageUpdate objects, making this
        # return value a list of lists
        updates_lol = run_hooks('frontpage_updates', limit=10)
        updates = sum(updates_lol, [])
        updates.sort(key=lambda obj: obj.time)

        c.updates = updates[0:10]

        return render('/index.mako')
