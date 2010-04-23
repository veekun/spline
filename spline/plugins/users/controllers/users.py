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

class UsersController(BaseController):

    def index(self):
        # Return a rendered template
        #   return render('/template.mako')
        # or, Return a response
        return 'stub'

    def view(self, id, name=None):
        """User page.

        URL is /users/id:name, where 'name' only exists for readability and is
        entirely optional and ignored.
        """

        c.page_user = meta.Session.query(model.User).get(id)
        if not c.page_user:
            abort(404)

        return render('/users/view.mako')
