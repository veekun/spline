"""Pylons environment configuration"""
import os

from mako.lookup import TemplateLookup
from pylons.error import handle_mako_error
from pylons import config
from sqlalchemy import engine_from_config

from spline.config.routing import make_map
import spline.lib.app_globals as app_globals
import spline.lib.helpers
from spline.lib.plugin import LocalPlugin
from spline.lib.plugin.load import load_plugins, run_hooks
import spline.model
from spline.model import init_model

def load_environment(global_conf, app_conf):
    """Configure the Pylons environment via the ``pylons.config``
    object
    """
    # Pylons paths
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    paths = dict(root=root,
                 controllers=os.path.join(root, 'controllers'),
                 static_files={},
                 templates=[os.path.join(root, 'templates')])

    # Initialize config with the basic options
    config.init_app(global_conf, app_conf, package='spline', paths=paths)

    # Create a fake plugin from the config dir if it's not the dir the core
    # spline code is running from
    extra_plugins = {}
    config_dir = os.path.dirname(global_conf['__file__'])
    if config_dir != root:
        extra_plugins['local'] = LocalPlugin(config_dir)

    # Load plugins before routing so we have a list of controllers
    load_plugins(paths, extra_plugins)
    # Add our static directory
    paths['static_files']['spline'] = os.path.join(root, 'public')
    
    config['routes.map'] = make_map()
    config['pylons.app_globals'] = app_globals.Globals()
    config['pylons.h'] = spline.lib.helpers

    # Create the Mako TemplateLookup, with the default auto-escaping
    config['pylons.app_globals'].mako_lookup = TemplateLookup(
        directories=paths['templates'],
        error_handler=handle_mako_error,
        module_directory=os.path.join(app_conf['cache_dir'], 'templates'),
        input_encoding='utf-8', output_encoding='utf-8',
        imports=['from webhelpers.html import escape'],
        default_filters=['escape'])
    
    # Setup SQLAlchemy database engine
    engine = engine_from_config(config, 'sqlalchemy.')
    init_model(engine)

    # CONFIGURATION OPTIONS HERE (note: all config options will override
    # any Pylons config options)

    # Use strict templating; none of this default-to-empty-string nonsense
    config['pylons.strict_c'] = True

    # Let plugins do any final setup
    run_hooks('after_setup')
