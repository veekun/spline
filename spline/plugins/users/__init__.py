from spline.lib.plugin import PluginBase

import controllers.accounts
import model

class UsersPlugin(PluginBase):
    def controllers(self):
        return dict(
            accounts = controllers.accounts.AccountsController,
        )

    def model(self):
        return [model.User, model.OpenID]
