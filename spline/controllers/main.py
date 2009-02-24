import logging

from pylons import request, response, session, tmpl_context as c
from pylons.controllers.util import abort, redirect_to

from spline.lib.base import BaseController, render
#from spline import model

log = logging.getLogger(__name__)

class MainController(BaseController):

    def index(self):
        return render('/index.mako')

    def css(self):
        # TODO: turn this into a cached concatenation of all CSS
        response.headers['Content-type'] = 'text/css; charset=utf-8'
        return render('/css/main.mako')
