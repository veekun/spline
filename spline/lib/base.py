"""The base Controller API

Provides the BaseController class for subclassing.
"""
from pylons import c
from pylons.controllers import WSGIController
from pylons.templating import render_mako as render

from spline.lib.plugin.load import run_hooks
from spline.model import meta

class BaseController(WSGIController):

    def __before__(self, action, **params):
        c.links = [
            ('Menu', dict(controller='main', action='index'), [
                ('Plugin 1', dict(controller='main', action='index'), [
                    ('foo', dict(controller='main', action='index'), []),
                    ('foo', dict(controller='main', action='index'), []),
                    ('foo', dict(controller='main', action='index'), []),
                    ('foo', dict(controller='main', action='index'), []),
                ]),
            ]),

        ]

        c.javascripts = [('spline', 'lib/jquery-1.3.2.min')]
        run_hooks('before_controller', action, **params)

    def __call__(self, environ, start_response):
        """Invoke the Controller"""
        # WSGIController.__call__ dispatches to the Controller method
        # the request is routed to. This routing information is
        # available in environ['pylons.routes_dict']
        try:
            return WSGIController.__call__(self, environ, start_response)
        finally:
            meta.Session.remove()
            run_hooks('after_controller')
