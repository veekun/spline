"""Helper functions

Consists of functions to typically be used within templates, but also
available to Controllers. This module is available to both as 'h'.
"""
from pylons import url
from webhelpers.html import escape, HTML, literal, url_escape
from webhelpers.html.tags import *

def static_uri(plugin_name, path):
    """Takes the name of a plugin and a path to a static file.

    Returns a full URI to the given file, as owned by the named plugin.
    """

    root_url = url('/')
    return "%sstatic/%s/%s" % (root_url, plugin_name, path)

# Import helpers as desired, or define your own, ie:
# from webhelpers.html.tags import checkbox, password
