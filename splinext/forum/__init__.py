from pkg_resources import resource_filename

from pylons import c, session

from spline.lib.plugin import PluginBase
from spline.lib.plugin import PluginBase, PluginLink, Priority

import splinext.forum.controllers.forum

def add_routes_hook(map, *args, **kwargs):
    """Hook to inject some of our behavior into the routes configuration."""
    require_POST = dict(conditions=dict(method=['POST']))

    map.connect('/forums', controller='forum', action='forums')
    map.connect('/forums/{forum_id}', controller='forum', action='threads')
    map.connect('/forums/{forum_id}/threads/{thread_id}', controller='forum', action='posts')

    map.connect('/forums/{forum_id}/threads/{thread_id}/write', controller='forum', action='write')


class ForumPlugin(PluginBase):
    def controllers(self):
        return dict(
            forum = splinext.forum.controllers.forum.ForumController,
        )

    def hooks(self):
        return [
            ('routes_mapping',    Priority.NORMAL,      add_routes_hook),
        ]
