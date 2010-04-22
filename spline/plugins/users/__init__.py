from pkg_resources import resource_filename

from pylons import c, session

from spline.lib.plugin import PluginBase
from spline.lib.plugin import PluginBase, PluginLink, Priority
import spline.model as model
import spline.model.meta as meta

import spline.plugins.users.controllers.accounts
import spline.plugins.users.model

def add_routes_hook(map, *args, **kwargs):
    """Hook to inject some of our behavior into the routes configuration."""
    map.connect('/accounts/login_begin', controller='accounts', action='login_begin')
    map.connect('/accounts/login_finish', controller='accounts', action='login_finish')
    map.connect('/accounts/logout', controller='accounts', action='logout')

def check_userid_hook(action, **params):
    """Hook to see if a user is logged in and, if so, stick a user object in
    c.
    """

    c.user = None

    if not 'user_id' in session:
        return

    user = meta.Session.query(model.User).get(session['user_id'])
    if not user:
        # Bogus id in the session somehow.  Clear it
        del session['user_id']
        session.save()
        return

    c.user = user


class UsersPlugin(PluginBase):
    def controllers(self):
        return dict(
            accounts = spline.plugins.users.controllers.accounts.AccountsController,
        )

    def model(self):
        return [
            spline.plugins.users.model.User,
            spline.plugins.users.model.OpenID,
        ]

    def template_dirs(self):
        return [
            (resource_filename(__name__, 'templates'), Priority.NORMAL)
        ]

    def hooks(self):
        return [
            ('routes_mapping',    Priority.NORMAL,      add_routes_hook),
            ('before_controller', Priority.VERY_FIRST,  check_userid_hook),
        ]

    def widgets(self):
        return [
            ('page_header', Priority.NORMAL, 'widgets/user_state.mako'),
        ]
