from pkg_resources import resource_filename

from pylons import session, tmpl_context as c
from routes import url_for as url

from spline.lib.plugin import PluginBase
from spline.lib.plugin import PluginBase, PluginLink, Priority

import splinext.forum.controllers.forum

def add_routes_hook(map, *args, **kwargs):
    """Hook to inject some of our behavior into the routes configuration."""
    require_GET = dict(conditions=dict(method=['GET']))
    require_POST = dict(conditions=dict(method=['POST']))

    map.connect('/forums', controller='forum', action='forums')
    map.connect(r'/forums/{forum_id:\d+}', controller='forum', action='threads')
    map.connect(r'/forums/{forum_id:\d+}/threads/{thread_id:\d+}', controller='forum', action='posts')

    map.connect(r'/forums/{forum_id:\d+}/write', controller='forum', action='write_thread', **require_GET)
    map.connect(r'/forums/{forum_id:\d+}/write', controller='forum', action='write_thread_commit', **require_POST)
    map.connect(r'/forums/{forum_id:\d+}/threads/{thread_id:\d+}/write', controller='forum', action='write', **require_GET)
    map.connect(r'/forums/{forum_id:\d+}/threads/{thread_id:\d+}/write', controller='forum', action='write_commit', **require_POST)


class ForumPlugin(PluginBase):
    def controllers(self):
        return dict(
            forum = splinext.forum.controllers.forum.ForumController,
        )

    def links(self):
        return [
            PluginLink(u'Forums', url(controller='forum', action='forums')),
        ]

    def hooks(self):
        hooks = [
            ('routes_mapping',    Priority.NORMAL,      add_routes_hook),
        ]

        # frontpage plugin may or may not be installed
        try:
            from splinext.forum.frontpage_sources import ForumSource, forum_activity
            hooks.append(
                ('frontpage_updates_forum', Priority.NORMAL, ForumSource))
            hooks.append(
                ('frontpage_extras', Priority.NORMAL, forum_activity))
        except ImportError:
            pass

        return hooks
