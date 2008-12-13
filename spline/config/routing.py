"""Routes configuration

The more specific and detailed routes should be defined first so they
may take precedent over the more generic routes. For more information
refer to the routes manual at http://routes.groovie.org/docs/
"""
from pylons import config
from routes import Mapper
from routes.util import controller_scan as dir_controller_scan

def controller_scan(directory):
    """Looks for a controller in the plugin list, defaulting to the usual
    Routes directory scan if it isn't found."""

    controllers = config['spline.plugins.controllers'].keys()
    controllers.extend(dir_controller_scan(directory))
    return controllers

def make_map():
    """Create, configure and return the routes Mapper"""
    map = Mapper(controller_scan=controller_scan,
                 directory=config['pylons.paths']['controllers'],
                 always_scan=config['debug'])
    map.minimization = False
    
    # The ErrorController route (handles 404/500 error pages); it should
    # likely stay at the top, ensuring it can always be resolved
    map.connect('/error/{action}', controller='error')
    map.connect('/error/{action}/{id}', controller='error')

    # Reasonable defaults; may or may not hang around
    map.connect('/', controller='index', action='index')
    map.connect('/{controller}', action='index')
    map.connect('/{controller}/{action}')
    map.connect('/{controller}/{action}/{id}')

    return map
