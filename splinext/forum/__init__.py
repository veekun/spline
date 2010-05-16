from pkg_resources import resource_filename

from pylons import c, session

from spline.lib.plugin import PluginBase
from spline.lib.plugin import PluginBase, PluginLink, Priority
import spline.model as model
import spline.model.meta as meta

import splinext.forum.controllers.forum
import splinext.forum.model

def add_routes_hook(map, *args, **kwargs):
    """Hook to inject some of our behavior into the routes configuration."""
    map.connect('/forums', controller='forum', action='forums')
    map.connect('/forums/{forum_id}', controller='forum', action='threads')
    map.connect('/forums/{forum_id}/threads/{thread_id}', controller='forum', action='posts')


class ForumPlugin(PluginBase):
    def controllers(self):
        return dict(
            forum = splinext.forum.controllers.forum.ForumController,
        )

    def model(self):
        return [
            model.Forum,
            model.Thread,
            model.Post,
        ]

    def template_dirs(self):
        return [
            (resource_filename(__name__, 'templates'), Priority.NORMAL)
        ]

    def hooks(self):
        return [
            ('routes_mapping',    Priority.NORMAL,      add_routes_hook),
        ]
