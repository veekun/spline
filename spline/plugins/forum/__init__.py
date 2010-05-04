from pkg_resources import resource_filename

from pylons import c, session

from spline.lib.plugin import PluginBase
from spline.lib.plugin import PluginBase, PluginLink, Priority
import spline.model as model
import spline.model.meta as meta

import spline.plugins.forum.controllers.forum
import spline.plugins.forum.model

def add_routes_hook(map, *args, **kwargs):
    """Hook to inject some of our behavior into the routes configuration."""
    map.connect('/forum', controller='forum', action='index')


class ForumPlugin(PluginBase):
    def controllers(self):
        return dict(
            forum = spline.plugins.forum.controllers.forum.ForumController,
        )

    def template_dirs(self):
        return [
            (resource_filename(__name__, 'templates'), Priority.NORMAL)
        ]

    def hooks(self):
        return [
            ('routes_mapping',    Priority.NORMAL,      add_routes_hook),
        ]
