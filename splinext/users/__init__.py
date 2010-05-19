from pkg_resources import resource_filename

from pylons import c, session

from spline.lib.plugin import PluginBase
from spline.lib.plugin import PluginBase, PluginLink, Priority
import spline.model.meta as meta

import splinext.users.controllers.accounts
import splinext.users.controllers.users
from splinext.users import model as users_model

def add_routes_hook(map, *args, **kwargs):
    """Hook to inject some of our behavior into the routes configuration."""
    # Login, logout
    map.connect('/accounts/login', controller='accounts', action='login')
    map.connect('/accounts/login_begin', controller='accounts', action='login_begin')
    map.connect('/accounts/login_finish', controller='accounts', action='login_finish')
    map.connect('/accounts/logout', controller='accounts', action='logout')

    # Self-admin
    map.connect('/users/{id};{name}/edit', controller='users', action='profile_edit')

    # Public user pages
    map.connect('/users', controller='users', action='list')
    map.connect('/users/{id};{name}', controller='users', action='profile')
    map.connect('/users/{id}', controller='users', action='profile')

def check_userid_hook(action, **params):
    """Hook to see if a user is logged in and, if so, stick a user object in
    c.
    """

    if not 'user_id' in session:
        c.user = users_model.AnonymousUser()
        return

    user = meta.Session.query(users_model.User).get(session['user_id'])
    if not user:
        # Bogus id in the session somehow.  Clear it
        del session['user_id']
        session.save()

        c.user = users_model.AnonymousUser()
        return

    c.user = user


class UsersPlugin(PluginBase):
    def controllers(self):
        return dict(
            accounts = splinext.users.controllers.accounts.AccountsController,
            users = splinext.users.controllers.users.UsersController,
        )

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
