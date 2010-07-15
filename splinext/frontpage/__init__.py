from pkg_resources import resource_filename

from spline.lib.plugin import PluginBase
from spline.lib.plugin import PluginBase, PluginLink, Priority

import splinext.frontpage.controllers.frontpage

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
            ('routes_mapping',    Priority.NORMAL,      add_routes_hook),
        ]
