"""The base Controller API

Provides the BaseController class for subclassing.
"""
from datetime import datetime, timedelta

from pylons import c, config
from pylons.controllers import WSGIController
from pylons.templating import render_mako as render
from sqlalchemy.interfaces import ConnectionProxy

from spline.lib.plugin.load import run_hooks
from spline.model import meta


class SQLATimerProxy(ConnectionProxy):
    """Simple connection proxy that keeps track of total time spent querying.
    """
    # props: http://techspot.zzzeek.org/?p=31
    def cursor_execute(self, execute, cursor, statement, parameters, context, executemany):
        now = datetime.now()
        try:
            return execute(cursor, statement, parameters, context)
        finally:
            if c and hasattr(c, 'timer'):
                delta = datetime.now() - now
                c.timer.sql_time += delta
                c.timer.sql_queries += 1

class ResponseTimer(object):
    """Nearly trivial class, used for tracking how long the page took to
    create.

    Properties are `total_time`, `sql_time`, and `sql_queries`.
    """

    def __init__(self):
        self._start_time = datetime.now()
        self._total_time = None

        # SQLAlchemy will add to these using the above proxy class; see
        # spline.config.environment
        self.sql_time = timedelta()
        self.sql_queries = 0

    @property
    def total_time(self):
        # Calculate and save the total render time as soon as this is accessed
        if self._total_time is None:
            self._total_time = datetime.now() - self._start_time
        return self._total_time


class BaseController(WSGIController):

    def __before__(self, action, **params):
        # Let templates get at the total render time
        c.timer = ResponseTimer()

        c.links = config['spline.plugins.links']
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
