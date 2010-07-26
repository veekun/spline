import logging
from openid.consumer.consumer import Consumer, SUCCESS, CANCEL
from openid.extensions.sreg import SRegRequest, SRegResponse
from openid.store.filestore import FileOpenIDStore
from openid.yadis.discover import DiscoveryFailure
from sqlalchemy.orm.exc import NoResultFound

from pylons import config, request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect_to
from routes import request_config

from spline.model import meta
from spline.lib import helpers as h
from spline.lib.base import BaseController, render
from splinext.users import model as users_model

log = logging.getLogger(__name__)

class AccountsController(BaseController):

    openid_store = FileOpenIDStore('/var/tmp')

    def _bail(self, reason):
        # Used for bailing on a login attempt; reshows the login page
        c.error = reason
        c.attempted_openid = request.params.get('openid_identifier', '')
        return render('/users/login.mako')


    def login(self):
        c.error = None
        c.attempted_openid = None
        return render('/users/login.mako')

    def login_begin(self):
        """Step one of logging in with OpenID; we redirect to the provider"""

        cons = Consumer(session=session, store=self.openid_store)

        try:
            openid_url = request.params['openid_identifier']
        except KeyError:
            return self._bail("Gotta enter an OpenID to log in.")

        try:
            auth_request = cons.begin(openid_url)
        except DiscoveryFailure:
            return self._bail(
                "Can't connect to '{0}'.  You sure it's an OpenID?"
                .format(openid_url)
            )

        sreg_req = SRegRequest(optional=['nickname', 'email', 'dob', 'gender',
                                         'country', 'language', 'timezone'])
        auth_request.addExtension(sreg_req)

        host = request.headers['host']
        protocol = request_config().protocol
        return_url = url(host=host, controller='accounts', action='login_finish')
        new_url = auth_request.redirectURL(return_to=return_url,
                                           realm=protocol + '://' + host)
        redirect_to(new_url)

    def login_finish(self):
        """Step two of logging in; the OpenID provider redirects back here."""

        cons = Consumer(session=session, store=self.openid_store)
        host = request.headers['host']
        return_url = url(host=host, controller='accounts', action='login_finish')
        res = cons.complete(request.params, return_url)

        if res.status == CANCEL:
            # I guess..  just..  back to the homepage?
            h.flash(u"""Login canceled.""", icon='user-silhouette')
            redirect_to(url('/'))
        elif res.status != SUCCESS:
            return 'Error!  %s' % res.message

        try:
            # Grab an existing user record, if one exists
            q = meta.Session.query(users_model.User) \
                    .filter(users_model.User.openids.any(openid=res.identity_url))
            user = q.one()
        except NoResultFound:
            # Try to pull a name out of the SReg response
            sreg_res = SRegResponse.fromSuccessResponse(res)
            try:
                username = sreg_res['nickname']
            except (KeyError, TypeError):
                # KeyError if sreg has no nickname; TypeError if sreg is None
                username = 'Anonymous'

            # Create db records
            user = users_model.User(name=username)
            meta.Session.add(user)

            openid = users_model.OpenID(openid=res.identity_url)
            user.openids.append(openid)

            meta.Session.commit()

        # Remember who's logged in, and we're good to go
        session['user_id'] = user.id
        session.save()

        h.flash(u"""Hello, {0}!""".format(user.name),
                icon='user')

        redirect_to('/', _code=303)

    def logout(self):
        """Logs the user out."""

        if 'user_id' in session:
            del session['user_id']
            session.save()

            h.flash(u"""Logged out.""",
                    icon='user-silhouette')

        redirect_to('/', _code=303)
