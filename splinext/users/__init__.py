from pkg_resources import resource_filename

from pylons import config, session, tmpl_context as c

from spline.lib.plugin import PluginBase, PluginLink, Priority
import spline.model.meta as meta

import splinext.users.controllers.accounts
import splinext.users.controllers.admin
import splinext.users.controllers.users
from splinext.users import model as users_model

def add_routes_hook(map, *args, **kwargs):
    """Hook to inject some of our behavior into the routes configuration."""
    require_GET = dict(conditions=dict(method=['GET']))
    require_POST = dict(conditions=dict(method=['POST']))

    # Login, logout
    map.connect('/accounts/login', controller='accounts', action='login')
    map.connect('/accounts/login_begin', controller='accounts', action='login_begin')
    map.connect('/accounts/login_finish', controller='accounts', action='login_finish')
    map.connect('/accounts/logout', controller='accounts', action='logout')

    # Self-admin
    map.connect(r'/users/{id:\d+};{name}/edit', controller='users', action='profile_edit', **require_GET)
    map.connect(r'/users/{id:\d+};{name}/edit', controller='users', action='profile_edit_commit', **require_POST)

    # Public user pages
    map.connect('/users', controller='users', action='list')
    map.connect(r'/users/{id:\d+};{name}', controller='users', action='profile')
    map.connect(r'/users/{id:\d+}', controller='users', action='profile')

    # Big-boy admin
    map.connect('/admin/users/permissions', controller='admin_users', action='permissions')

def monkeypatch_user_hook(config, *args, **kwargs):
    """Hook to tell the `User` model who the root user is."""
    try:
        users_model.User._root_user_id \
            = int(config['spline-users.root_user_id'])
    except KeyError:
        # No config set; oh well!
        pass

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
            admin_users = splinext.users.controllers.admin.AdminController,
            users = splinext.users.controllers.users.UsersController,
        )

    def template_dirs(self):
        return [
            (resource_filename(__name__, 'templates'), Priority.NORMAL)
        ]

    def hooks(self):
        return [
            ('routes_mapping',    Priority.NORMAL,      add_routes_hook),
            ('after_setup',       Priority.NORMAL,      monkeypatch_user_hook),
            ('before_controller', Priority.VERY_FIRST,  check_userid_hook),
        ]

    def widgets(self):
        return [
            ('page_header', Priority.NORMAL, 'widgets/user_state.mako'),
        ]
