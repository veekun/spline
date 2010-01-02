"""Routes configuration

The more specific and detailed routes should be defined first so they
may take precedent over the more generic routes. For more information
refer to the routes manual at http://routes.groovie.org/docs/
"""
import os

from pylons import config
from routes import Mapper
from routes.util import controller_scan as dir_controller_scan

from spline.lib.plugin.load import run_hooks

def controller_scan(directory):
    """Looks for a controller in the plugin list, defaulting to the usual
    Routes directory scan if it isn't found."""

    controllers = config['spline.plugins.controllers'].keys()
    controllers.extend(dir_controller_scan(directory))
    return controllers

def make_map(content_dirs=[]):
    """Create, configure and return the routes Mapper"""
    map = Mapper(controller_scan=controller_scan,
                 directory=config['pylons.paths']['controllers'],
                 always_scan=config['debug'])
    map.minimization = False

    # Content files get explicitly mapped so we don't have to pull any cheap
    # tricks like looking for them in a 404 handler.  We do them first so
    # controllers can't be clobbered by bad choices of filenames
    for content_dir in content_dirs:
        for root, dirs, files in os.walk(content_dir):
            for name in files:
                localpath = os.path.join(root, name)
                webpath, ext = os.path.splitext(localpath)

                # Skip over hidden files.
                # For now, also require a .html extension.
                if webpath[0] == '.' or ext != '.html':
                    continue

                # Use the full path as a route name so url() can easily route
                # to a static page
                map.connect('/' + os.path.relpath(webpath, root),
                            '/' + os.path.relpath(webpath, root),
                            controller='main', action='content', path=localpath)

    # The ErrorController route (handles 404/500 error pages); it should
    # likely stay at the top, ensuring it can always be resolved
    map.connect('/error/{action}', controller='error')
    map.connect('/error/{action}/{id}', controller='error')

    map.connect('/css', controller='main', action='css')

    # Allow plugins to map routes without the below defaults clobbering them
    run_hooks('routes_mapping', map=map)

    map.connect('/', controller='main', action='index')

    return map
