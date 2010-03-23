"""Pylons middleware initialization"""
from beaker.middleware import CacheMiddleware, SessionMiddleware
from paste import request as paste_request
from paste.cascade import Cascade
from paste.registry import RegistryManager
from paste.urlparser import StaticURLParser
from paste.deploy.converters import asbool
from pylons import config
from pylons.middleware import ErrorHandler, StatusCodeRedirect
from pylons.wsgiapp import PylonsApp
from routes.middleware import RoutesMiddleware

from spline.config.environment import load_environment

class SplineApp(PylonsApp):
    def find_controller(self, controller):
        """Controller search method that scans the plugin controller list,
        falling back to the default Pylons way if it's not found."""

        try:
            return config['spline.plugins.controllers'][controller]
        except KeyError:
            return super(SplineApp, self).find_controller(controller)

class SplineStaticURLParser(object):
    """Creates a URL parser that handles finding any plugin's static files.

    Assumes URLs to static files are of the form /static/:plugin_name/:uri.
    """

    def __init__(self, static_paths={}):
        """Constructor.

        static_paths -- a dictionary mapping plugin identifiers (used in static
            file URIs) to the paths where those plugins' static files reside
        """

        self.static_paths = static_paths
        self.url_parsers = {}
        for plugin_name, path in self.static_paths.items():
            self.url_parsers[plugin_name] = StaticURLParser(path)

        if not 'spline' in self.url_parsers:
            raise ValueError("A default 'spline' static path is required.")

        self.default_parser = self.url_parsers['spline']

    def __call__(self, environ, start_response):
        """The meat of this operation.  Dispatches to the StaticURLParser for
        the plugin named in the URL.
        """

        # Need to match /static/:plugin_name/
        path_static = paste_request.path_info_pop(environ)
        if path_static != 'static':
            return self.default_parser.not_found(environ, start_response)

        plugin_name = paste_request.path_info_pop(environ)
        if plugin_name not in self.url_parsers:
            return self.default_parser.not_found(environ, start_response)

        return self.url_parsers[plugin_name](environ, start_response)

def make_app(global_conf, full_stack=True, **app_conf):
    """Create a Pylons WSGI application and return it

    ``global_conf``
        The inherited configuration for this application. Normally from
        the [DEFAULT] section of the Paste ini file.

    ``full_stack``
        Whether or not this application provides a full WSGI stack (by
        default, meaning it handles its own exceptions and errors).
        Disable full_stack when this application is "managed" by
        another WSGI middleware.

    ``app_conf``
        The application's local configuration. Normally specified in
        the [app:<name>] section of the Paste ini file (where <name>
        defaults to main).

    """
    # Configure the Pylons environment
    load_environment(global_conf, app_conf)

    # The Pylons WSGI app
    app = SplineApp()

    # CUSTOM MIDDLEWARE HERE (filtered by error handling middlewares)

    # Routing/Session/Cache Middleware
    app = RoutesMiddleware(app, config['routes.map'])
    app = SessionMiddleware(app, config)
    app = CacheMiddleware(app, config)

    # Super ultra debug mode
    #from paste.translogger import TransLogger
    #app = TransLogger(app)

    if asbool(full_stack):
        # Handle Python exceptions
        app = ErrorHandler(app, global_conf, **config['pylons.errorware'])

        # Display error documents for 401, 403, 404 status codes (and
        # 500 when debug is disabled)
        if asbool(config['debug']):
            app = StatusCodeRedirect(app)
        else:
            app = StatusCodeRedirect(app, [400, 401, 403, 404, 500])

    # Establish the Registry for this application
    app = RegistryManager(app)

    # Static files (If running in production, and Apache or another web 
    # server is handling this static content, remove the following 2 lines)
    static_app = SplineStaticURLParser(config['pylons.paths']['static_files'])
    app = Cascade([static_app, app])
    return app
