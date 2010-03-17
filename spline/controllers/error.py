from pylons import request, tmpl_context as c

from spline.lib.base import BaseController, render

class ErrorController(BaseController):
    """Generates error documents as and when they are required.

    The ErrorDocuments middleware forwards to ErrorController when error
    related status codes are returned from the application.

    This behaviour can be altered by changing the parameters to the
    ErrorDocuments middleware in your config/middleware.py file.
    """

    def document(self):
        """Render the error document."""

        # code and messae might come from GET, *or* from the Pylons response
        # object.  They seem to come from the latter most of the time, but
        # let's be safe anyway.
        response = request.environ.get('pylons.original_response')

        c.message = request.GET.get('message', response and response.status)
        c.code    = request.GET.get('code',    response and response.status_int)
        c.code = int(c.code)
        return render('/error.mako')
