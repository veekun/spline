"""Pylons environment configuration"""
import os
import sys

from mako.lookup import TemplateLookup
import pylons
from pylons.configuration import PylonsConfig
from paste.deploy.converters import asbool
from pylons.error import handle_mako_error
from sqlalchemy import engine_from_config

from spline.config.routing import make_map
import spline.lib.base
import spline.lib.app_globals as app_globals
import spline.lib.helpers
from spline.lib.plugin import LocalPlugin
from spline.lib.plugin.load import load_plugins, run_hooks
import spline.model
from spline.model import init_model


def load_environment(global_conf, app_conf):
    """Configure the Pylons environment"""
    config = PylonsConfig()

    # Pylons paths
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    paths = dict(root=root,
                 controllers=os.path.join(root, 'controllers'),
                 static_files={},
                 content_files=[],
                 templates=[os.path.join(root, 'templates')])

    # Initialize config with the basic options
    config.init_app(global_conf, app_conf, package='spline', paths=paths)

    extra_plugins = {}
    config_dir = os.path.dirname(global_conf['__file__'])
    paths['local'] = config_dir
    if config_dir != root:
        # This app isn't running out of a vanilla spline checkout.  See if it
        # publishes its own local plugin class, and if not, create a generic
        # one
        original_path = sys.path
        sys.path = [config_dir]
        try:
            local_module = __import__('plugin')
            plugin_class = local_module.LocalPlugin
        except:
            plugin_class = LocalPlugin
        finally:
            # Restore path no matter what!
            sys.path = original_path
        extra_plugins['local'] = plugin_class(config_dir)

    # Load plugins before routing so we have a list of controllers
    load_plugins(config, paths, extra_plugins)
    # Add our static directory
    paths['static_files']['spline'] = os.path.join(root, 'public')

    config['routes.map'] = make_map(config, content_dirs=paths['content_files'])
    config['pylons.app_globals'] = app_globals.Globals(config)
    pylons.cache._push_object(config['pylons.app_globals'].cache)
    config['pylons.h'] = spline.lib.helpers

    # Create the Mako TemplateLookup, with the default auto-escaping
    module_directory = {}
    if 'cache_dir' in app_conf:
        module_directory['module_directory'] \
            = os.path.join(app_conf['cache_dir'], 'templates')
    config['pylons.app_globals'].mako_lookup = TemplateLookup(
        directories=paths['templates'],
        error_handler=handle_mako_error,
        input_encoding='utf-8', output_encoding='utf-8',
        imports=['from webhelpers.html import escape'],
        default_filters=['escape'],
        filesystem_checks=asbool(config.get('mako.filesystem_checks', True)),
        **module_directory)

    # Setup SQLAlchemy database engine
    # Proxy class is just to record query time; in debugging mode, it also
    # tracks every query
    config['spline.sql_debugging'] = asbool(
        config.get('spline.sql_debugging', False))
    if config['spline.sql_debugging']:
        sqla_proxy = spline.lib.base.SQLAQueryLogProxy()
    else:
        sqla_proxy = spline.lib.base.SQLATimerProxy()
    engine = engine_from_config(config, 'sqlalchemy.', proxy=sqla_proxy)
    init_model(engine)

    # CONFIGURATION OPTIONS HERE (note: all config options will override
    # any Pylons config options)

    # Use strict templating; none of this default-to-empty-string nonsense
    config['pylons.strict_c'] = True

    # Remove any stale cron lock
    del config['pylons.app_globals'].cache.get_cache('spline:cron')['LOCK']

    return config
