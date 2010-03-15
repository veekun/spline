from glob import glob
import logging
import os

from mako.template import Template
from pylons import config, request, response, session, tmpl_context as c
from pylons.controllers.util import abort, redirect_to
from pylons.templating import pylons_globals

from spline.lib.base import BaseController, render
#from spline import model

log = logging.getLogger(__name__)

class MainController(BaseController):

    def index(self):
        return render('/index.mako')


    def css(self):
        """Returns all the CSS in every plugin, concatenated."""
        # This solution sucks donkey balls, but it's marginally better than
        # loading every single stylesheet manually, so it stays until I have
        # a better idea
        response.headers['Content-type'] = 'text/css; charset=utf-8'

        # We want to let normal template overriding work here, so construct a
        # list of UNIQUE filenames by using a set
        css_files = set()

        # Go backwards through the list so we hit the higher-priority templates
        # LAST; this lets them override lower-priority style rules, as expected
        longass_key = 'spline.plugins.template_directories'
        for directory in reversed(config[longass_key]):
            for css_path in glob(os.path.join(directory, 'css', '*.mako')):
                (whatever, css_file) = os.path.split(css_path)
                css_files.add(css_file)

        stylesheets = []
        for css_file in sorted(css_files):
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
