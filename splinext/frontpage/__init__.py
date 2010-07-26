from collections import defaultdict, namedtuple
from pkg_resources import resource_filename
import re
import subprocess

from pylons import config

from spline.lib import helpers
from spline.lib.plugin import PluginBase, PluginLink, Priority
from spline.lib.plugin.load import run_hooks

import splinext.frontpage.controllers.frontpage
from splinext.frontpage.sources import FeedSource, GitSource

def add_routes_hook(map, *args, **kwargs):
    """Hook to inject some of our behavior into the routes configuration."""
    map.connect('/', controller='frontpage', action='index')

def load_sources_hook(*args, **kwargs):
    """Hook to load all the known sources and stuff them in config.  Run once,
    on server startup.
    """
    # Extract source definitions from config and store as source_name => config
    update_config = defaultdict(dict)
    key_rx = re.compile(
        '(?x) ^ spline-frontpage [.] sources [.] (\w+) (?: [.] (\w+) )? $')
    for key, val in config.iteritems():
        # Match against spline-frontpage.source.(source).(key)
        match = key_rx.match(key)
        if not match:
            continue

        source_name, subkey = match.groups()
        if not subkey:
            # This is the type declaration; use a special key
            subkey = '__type__'

        update_config[source_name][subkey] = val

    # Figure out the global limit and expiration time, with reasonable
    # defaults.  Make sure they're integers.
    global_limit = int(config.get('spline-frontpage.limit', 10))
    # max_age is optional and can be None
    try:
        global_max_age = int(config['spline-frontpage.max_age'])
    except KeyError:
        global_max_age = None

    config['spline-frontpage.limit'] = global_limit
    config['spline-frontpage.max_age'] = global_max_age

    # Ask plugins to turn configuration into source objects
    sources = []
    for source, source_config in update_config.iteritems():
        hook_name = 'frontpage_updates_' + source_config['__type__']
        del source_config['__type__']  # don't feed this to constructor!

        # Default to global limit and max age.  Source takes care of making
        # integers and whatnot
        source_config.setdefault('limit', global_limit)
        source_config.setdefault('max_age', global_max_age)

        # Hooks return a list of sources; combine with running list
        sources += run_hooks(hook_name, **source_config)

    # Save the list of sources, and done
    config['spline-frontpage.sources'] = sources

def source_cron_hook(*args, **kwargs):
    """Hook to pass on cron tics to all sources, should they need it for e.g.
    caching.
    """
    for source in config['spline-frontpage.sources']:
        source.do_cron(*args, **kwargs)

class FrontPagePlugin(PluginBase):
    def controllers(self):
        return dict(
            frontpage = splinext.frontpage.controllers.frontpage.FrontPageController,
        )

    def template_dirs(self):
        return [
            (resource_filename(__name__, 'templates'), Priority.FIRST)
        ]

    def hooks(self):
        return [
            ('routes_mapping',          Priority.NORMAL,    add_routes_hook),
            ('after_setup',             Priority.NORMAL,    load_sources_hook),
            ('cron',                    Priority.NORMAL,    source_cron_hook),
            ('frontpage_updates_rss',   Priority.NORMAL,    FeedSource),
            ('frontpage_updates_git',   Priority.NORMAL,    GitSource),
        ]
