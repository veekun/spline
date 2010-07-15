from pkg_resources import resource_filename

from pylons import c, session

from spline.lib.plugin import PluginBase
from spline.lib.plugin import PluginBase, PluginLink, Priority
from spline.model import meta

import splinext.forum.controllers.forum
from splinext.forum import model as forum_model

def add_routes_hook(map, *args, **kwargs):
    """Hook to inject some of our behavior into the routes configuration."""
    require_POST = dict(conditions=dict(method=['POST']))

    map.connect('/forums', controller='forum', action='forums')
    map.connect('/forums/{forum_id}', controller='forum', action='threads')
    map.connect('/forums/{forum_id}/threads/{thread_id}', controller='forum', action='posts')

    map.connect('/forums/{forum_id}/write', controller='forum', action='write_thread')
    map.connect('/forums/{forum_id}/threads/{thread_id}/write', controller='forum', action='write')

class FrontPageNewsPost(object):
    pass

def frontpage_hook(limit):
    """Hook to return recent news for the front page."""
    threads = meta.Session.query(forum_model.Thread) \
        .join(forum_model.Thread.first_post) \
        .order_by(forum_model.Post.posted_time.desc()) \
        [:limit]

    updates = []
    for thread in threads:
        update = FrontPageNewsPost()
        update.time = thread.first_post.posted_time
        update.template = '/forum/front_page.mako'
        update.post = thread.first_post
        updates.append(update)

    return updates


class ForumPlugin(PluginBase):
    def controllers(self):
        return dict(
            forum = splinext.forum.controllers.forum.ForumController,
        )

    def hooks(self):
        return [
            ('routes_mapping',    Priority.NORMAL,      add_routes_hook),
            ('frontpage_updates', Priority.NORMAL,      frontpage_hook),
        ]
