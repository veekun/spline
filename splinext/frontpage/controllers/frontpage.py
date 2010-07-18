from collections import defaultdict
import logging
import re

from pylons import config, request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect_to
from routes import request_config
from sqlalchemy.orm.exc import NoResultFound

from spline.lib import helpers as h
from spline.lib.base import BaseController, render
from spline.lib.plugin.load import run_hooks

log = logging.getLogger(__name__)

class FrontPageController(BaseController):

    def index(self):
        """Magicaltastic front page.

        Plugins can register a hook called 'frontpage_updates_<type>' to add
        updates to the front page.  `<type>` is an arbitrary string indicating
        the sort of update the plugin knows how to handle; for example,
        spline-forum has a `frontpage_updates_forum` hook for posting news from
        a specific forum.

        Hook handlers should return a list of FrontPageUpdate objects.

        Standard hook parameters are `limit`, the maximum number of items that
        should ever be returned.

        Updates are configured in the .ini like so:

            spline-frontpage.sources.foo = updatetype
            spline-frontpage.sources.foo.opt1 = val1
            spline-frontpage.sources.foo.opt2 = val2

        Note that the 'foo' name is completely arbitrary and is only used for
        grouping options together.  This will result in a call to:

            run_hooks('frontpage_updates_updatetype', opt1=val1, opt2=val2)

        Standard options are not shown and take precedence over whatever's in
        the config file.

        Local plugins can override the fairly simple index.mako template to
        customize the front page layout.
        """
        # XXX no reason to do this on the fly; cache it on server startup
        update_config = defaultdict(dict)  # source_name => config
        key_rx = re.compile(
            '(?x) ^ spline-frontpage [.] sources [.] (\w+) (?: [.] (\w+) )? $')
        for key, val in config.iteritems():
            match = key_rx.match(key)
            if not match:
                continue

            source_name, subkey = match.groups()
            if not subkey:
                # This is the type declaration; use a special key
                subkey = '__type__'

            update_config[source_name][subkey] = val


        global_config = dict(
            limit = 10,
        )

        # Ask plugins to deal with this stuff for us!
        updates = []
        for source, source_config in update_config.iteritems():
            source_config2 = source_config.copy()
            hook_name = 'frontpage_updates_' + source_config2.pop('__type__')
            source_config2.update(global_config)

            # Hooks should return a list of FrontPageUpdate objects, making this
            # return value a list of lists
            updates_lol = run_hooks(hook_name, **source_config2)
            updates += sum(updates_lol, [])

        # Sort everything by descending time, then crop to the right number of
        # items
        updates.sort(key=lambda obj: obj.time)
        updates.reverse()
        c.updates = updates[:global_config['limit']]

        return render('/index.mako')
