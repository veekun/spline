from collections import defaultdict
import datetime
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

        Standard hook parameters are:
        `limit`, the maximum number of items that should ever be returned.
        `max_age`, the number of seconds after which items expire.
        `title`, a name for the source.
        `icon`, an icon to show next to its name.

        `limit` and `max_age` are also global options.

        Updates are configured in the .ini like so:

            spline-frontpage.sources.foo = updatetype
            spline-frontpage.sources.foo.opt1 = val1
            spline-frontpage.sources.foo.opt2 = val2

        Note that the 'foo' name is completely arbitrary and is only used for
        grouping options together.  This will result in a call to:

            run_hooks('frontpage_updates_updatetype', opt1=val1, opt2=val2)

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

            if subkey in ('limit', 'max_age'):
                val = int(val)
            update_config[source_name][subkey] = val

        global_limit = int(config.get('spline-frontpage.limit', 10))
        now = datetime.datetime.now()
        try:
            global_max_age = now - datetime.timedelta(
                seconds=int(config['spline-frontpage.max_age']))
        except KeyError:
            global_max_age = None

        # Ask plugins to deal with this stuff for us!
        updates = []
        for source, source_config in update_config.iteritems():
            hook_name = 'frontpage_updates_' + source_config['__type__']

            # Merge with the global config
            merged_config = source_config.copy()
            del merged_config['__type__']

            merged_config['limit'] = min(
                merged_config.get('limit', global_limit),
                global_limit,
            )

            try:
                local_max_age = now - datetime.timedelta(
                    seconds=merged_config['max_age'])
            except KeyError:
                local_max_age = None

            if global_max_age and local_max_age:
                merged_config['max_age'] = max(global_max_age, local_max_age)
            else:
                merged_config['max_age'] = global_max_age or local_max_age

            # XXX bleh
            updates_lol = run_hooks(hook_name, **merged_config)
            source_obj = updates_lol[0]
            updates += source_obj.poll(merged_config['limit'], merged_config['max_age'])

            # Little optimization: maximum age effectively becomes the age of
            # the oldest thing that would still appear on the page, as anything
            # older would drop off the end no matter what.
            # So sort by descending time and crop each iteration...
            updates.sort(key=lambda obj: obj.time, reverse=True)
            updates = updates[:global_limit]

            if updates and len(updates) == global_limit:
                global_max_age = updates[-1].time

        c.updates = updates

        return render('/index.mako')
