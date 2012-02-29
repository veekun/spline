"""The base Controller API

Provides the BaseController class for subclassing.
"""
from collections import defaultdict
from datetime import datetime, timedelta
import traceback
import zlib

from mako.runtime import capture
from pylons import cache, config, tmpl_context as c
from pylons.controllers import WSGIController
from pylons.templating import render_mako as render
from pylons.i18n.translation import set_lang
from sqlalchemy.interfaces import ConnectionProxy

from spline.lib.plugin.load import run_hooks
from spline.model import meta


class SQLATimerProxy(ConnectionProxy):
    """Simple connection proxy that keeps track of total time spent querying.
    """
    # props: http://techspot.zzzeek.org/?p=31
    def cursor_execute(self, execute, cursor, statement, parameters, context, executemany):
        try:
            return execute(cursor, statement, parameters, context)
        finally:
            try:
                c.timer.sql_queries += 1
            except (TypeError, AttributeError):
                # Might happen if SQL is run before Pylons is done starting
                pass

    def execute(self, conn, execute, clauseelement, *args, **kwargs):
        now = datetime.now()
        try:
            return execute(clauseelement, *args, **kwargs)
        finally:
            try:
                delta = datetime.now() - now
                c.timer.sql_time += delta
            except (TypeError, AttributeError):
                pass

class SQLAQueryLogProxy(SQLATimerProxy):
    """Extends the above to also log a summary of exactly what queries were
    executed, what userland code triggered them, and how long each one took.
    """
    def cursor_execute(self, execute, cursor, statement, parameters, context, executemany):
        now = datetime.now()
        try:
            super(SQLAQueryLogProxy, self).cursor_execute(
                execute, cursor, statement, parameters, context, executemany)
        finally:
            try:
                # Find who spawned this query.  Rewind up the stack until we
                # escape from sqlalchemy code -- including this file, which
                # contains proxy stuff
                caller = '(unknown)'
                for frame_file, frame_line, frame_func, frame_code in \
                    reversed(traceback.extract_stack()):

                    if __file__.startswith(frame_file) or \
                        '/sqlalchemy/' in frame_file or \
                        'db/multilang.py' in frame_file:

                        continue

                    # OK, this is it
                    caller = "{0}:{1} in {2}".format(
                        frame_file, frame_line, frame_func)
                    break

                c.timer.sql_query_log[statement].append(dict(
                    parameters=parameters,
                    time=datetime.now() - now,
                    caller=caller,
                ))
            except (TypeError, AttributeError):
                pass

class ResponseTimer(object):
    """Nearly trivial class, used for tracking how long the page took to
    create.

    Properties are `total_time`, `sql_time`, and `sql_queries`.

    In SQL debug mode, `sql_query_log` is also populated.  Its keys are
    queries; values are dicts of parameters, time, and caller.
    """

    def __init__(self):
        self._start_time = datetime.now()
        self._total_time = None

        self.from_cache = None

        # SQLAlchemy will add to these using the above proxy class; see
        # spline.config.environment
        self.sql_time = timedelta()
        self.sql_queries = 0
        self.sql_query_log = defaultdict(list)

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
        c.javascripts = [
            ('spline', 'lib/jquery-1.7.1.min'),
            ('spline', 'lib/jquery.cookies-2.2.0.min'),
            ('spline', 'lib/jquery.ui-1.8.4.min'),
            ('spline', 'core'),
        ]
        run_hooks('before_controller', action, **params)

    def __call__(self, environ, start_response):
        """Invoke the Controller"""
        # WSGIController.__call__ dispatches to the Controller method
        # the request is routed to. This routing information is
        # available in environ['pylons.routes_dict']

        c.lang = environ['pylons.routes_dict'].get('_lang')
        if c.lang:
            set_lang(c.lang)

        try:
            return WSGIController.__call__(self, environ, start_response)
        finally:
            meta.Session.remove()

    def __after__(self, **params):
        run_hooks('after_controller', **params)

    def cache_content(self, key, do_work, template):
        """Argh!

        Okay, so.  Use this when you want to cache the BODY of a page but not
        the CHROME (i.e., wrapper or base or whatever).

        ``key``
            The key that uniquely identifies this particular rendering of this
            page content.

        ``do_work``
            Some function that will stuff a bunch of expensive data in c.  This
            will only be called if the page hasn't yet been cached.  It'll be
            passed the key.

        ``template``
            Name of the template to use.

        Also, DO NOT FORGET TO wrap the cachable part of your template in a
        <%lib:cache_content> tag, or nothing will get cached!

        If a page body is pulled from cache, c.timer.from_cache will be set to
        True.  If the page had to be generated, it will be set to False.  (If
        this function wasn't involved at all, it will be set to None.)
        """

        # Content needs to be cached per-language
        key = u"{0}/{1}".format(key, c.lang)

        # Cache for...  ten hours?  Sure, whatever
        content_cache = cache.get_cache('content_cache:' + template,
                                        expiretime=36000)

        # XXX This is dumb.  Caches don't actually respect the 'enabled'
        # setting, so we gotta fake it.
        if not content_cache.nsargs.get('enabled', True):
            def skip_cache(context, mako_def):
                do_work(key)
                mako_def.body()
            c._cache_me = skip_cache
            return render(template)

        # These pages can be pretty big.  In the case of e.g. memcached, that's
        # a lot of RAM spent on giant pages that consist half of whitespace.
        # Solution: gzip everything.  Use level 1 for speed!
        def cache_me(context, mako_def):
            c.timer.from_cache = True

            def generate_page():
                c.timer.from_cache = False
                do_work(key)
                return zlib.compress(
                    capture(context, mako_def.body).encode('utf8'),
                    1
                )

            context.write(
                zlib.decompress(
                    content_cache.get_value(key=key, createfunc=generate_page)
                ).decode('utf8')
            )

        c._cache_me = cache_me

        return render(template)
