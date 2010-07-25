from collections import namedtuple
import datetime
from pkg_resources import resource_filename
import subprocess

from spline.lib import helpers
from spline.lib.plugin import PluginBase, PluginLink, Priority

import splinext.frontpage.controllers.frontpage
from splinext.frontpage.sources import FeedSource, GitSource

def add_routes_hook(map, *args, **kwargs):
    """Hook to inject some of our behavior into the routes configuration."""
    map.connect('/', controller='frontpage', action='index')


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
            ('frontpage_updates_rss',   Priority.NORMAL,    FeedSource),
            ('frontpage_updates_git',   Priority.NORMAL,    GitSource),
        ]
