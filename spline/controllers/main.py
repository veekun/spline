from glob import glob
import logging
import os

from pylons import config, request, response, session, tmpl_context as c
from pylons.controllers.util import abort, redirect_to

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

        for directory in config['pylons.app_globals'].mako_lookup.directories:
            for css_path in glob(os.path.join(directory, 'css', '*.mako')):
                (whatever, css_file) = os.path.split(css_path)
                css_files.add(css_file)

        full_stylesheet = ''
        for css_file in sorted(css_files):
            full_stylesheet += render("/css/%s" % css_file)

        return full_stylesheet
