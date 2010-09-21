import datetime
import logging

from mako.template import Template
from pylons import cache, config, request, response, session, tmpl_context as c
from pylons.controllers.util import abort, redirect
from pylons.templating import pylons_globals

from spline.lib.base import BaseController, render
from spline.lib.plugin.load import run_hooks

log = logging.getLogger(__name__)

class MainController(BaseController):

    def index(self):
        """Blank front page.  Local plugin or the frontpage plugin can override
        it.
        """
        return render('/index.mako')


    def css(self):
        """Returns all the CSS in every plugin, concatenated."""
        # This solution sucks donkey balls, but it's marginally better than
        # loading every single stylesheet manually, so it stays until I have
        # a better idea
        response.headers['Content-type'] = 'text/css; charset=utf-8'

        stylesheets = []
        for css_file in config['spline.plugins.stylesheets']:
            stylesheets.append(render("/css/%s" % css_file))

        return '\n'.join(stylesheets)


    def content(self, path):
        """Handles returning "content" files: static content shoved more or
        less verbatim into the wrapper.
        """
        # Static files need to go through Mako to e.g. set their titles and
        # generate links, but TemplateLookup will not fetch templates outside
        # its known template directories.
        # Instead, load the template manually, and use the same lookup object
        # as everything else so references to other templates can still work
        # XXX when there's a real cache mechanism, this should use it!
        lookup = config['pylons.app_globals'].mako_lookup
        template = Template(filename=path, lookup=lookup,
                            **lookup.template_args)
        return template.render_unicode(**pylons_globals())


    def cron(self):
        """Runs interested cron-jobs."""
        cron_cache = cache.get_cache('spline:cron')

        # XXX Tiny race condition here; checking for a value and then setting
        # it is not atomic
        if 'LOCK' in cron_cache:
            return 'already running'
        cron_cache['LOCK'] = 1
        try:
            now = datetime.datetime.now().time()
            tic = now.hour * 60 + now.minute
            run_hooks('cron', tic=tic)

        finally:
            # Always unlock when done
            del cron_cache['LOCK']

        return 'ok'
