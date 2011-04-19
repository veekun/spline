import logging

from pylons import config, request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect

from spline.model import meta
from spline.lib.base import BaseController, render
from splinext.users import model as users_model

log = logging.getLogger(__name__)


class AdminController(BaseController):

    def permissions(self):
        if not c.user.can('administrate'):
            abort(403)

        c.roles = meta.Session.query(users_model.Role) \
            .order_by(users_model.Role.id.asc()).all()
        return render('/users/admin/permissions.mako')
