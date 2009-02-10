from pylons import c, session

from spline.lib.plugin import PluginBase
import spline.model as model
import spline.model.meta as meta

import controllers.accounts
import model as user_model

def check_userid_hook(action, **params):
    """Hook to see if a user is logged in and, if so, stick a user object in
    c.
    """

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
            accounts = controllers.accounts.AccountsController,
        )

    def model(self):
        return [user_model.User, user_model.OpenID]

    def hooks(self):
        return [
            ('before_controller', 1, check_userid_hook),
        ]
