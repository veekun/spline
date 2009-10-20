"""Functionality generally needed to build a plugin."""
from collections import namedtuple
import os.path

PluginLink = namedtuple('PluginLink', ['label', 'route'])

class Priority(object):
    """Enum for the order in which to load various components."""
    VERY_FIRST  = 1
    FIRST       = 2
    NORMAL      = 3
    LAST        = 4
    VERY_LAST   = 5

class PluginLink(object):
    """Represents a link in a plugin."""

    # Pseudo-global dictionary of all seen urls mapped to their respective link
    # objects.  Used for breadcrumbs, et al.  Hopefully there are no conceptual
    # problems with this.
    url_lookup = dict()

    def __init__(self, label, url=None, children=[], collapsed=False):
        """Arguments:

        `label`
            Label for this link.

        `url`
            URL for this link.  If omitted, this link may serve as merely a
            header instead.

        `children`
            An optional list of PluginLink objects.

        `collapsed`
            Whether this link appears on the menu.  It will still appear in a
            table of contents.
        """

        self.label = label
        self.url = url
        self.children = children
        self.collapsed = collapsed

        # Make this tree bidirectional
        self.parent = None
        for child in children:
            child.parent = self

        # Remember the link's position in the tree
        if url:
            self.url_lookup[url] = self


class PluginBase(object):
    """Base object for spline plugins.  Plugins should advertise a subclass of
    this class as an entry point.
    """

    def __init__(self):
        pass

    def controllers(self):
        """Returns a dictionary mapping routing names to controllers."""
        return {}

    def template_dirs(self):
        """Returns a list of directories containing templates.

        Each element of this list should be a tuple of (directory, priority).
        """
        return []

    def static_dir(self):
        """Returns a directory containing static files, or None for none."""
        return None

    def content_dir(self):
        """Returns a directory containing content files, or None for none."""
        return None

    def model(self):
        """Returns a list of classes to stick in Spline's model namespace.

        Please be sure to list ALL model classes here; otherwise, the rest of
        the app will have trouble finding them, which can be important for
        things like creating all new tables as InnoDB.
        """
        return []

    def hooks(self):
        """Returns a list of tuples in the form `(hook_name, priority, function)`.

        A hook is a named point within Python code that allows plugins to
        inject their own code; for example, there is a `before_controller` hook
        that plugins can use to execute code before each controller call.  The
        `users` plugin uses this to check the session for a logged-in user on
        each request.

        `hook_name` is a string identifying a hook somewhere in either Spline
        core or another plugin.
        `priority` is a number from 1 to 5 using Apache conventions: 3 is
        normal, 2/4 are first/last, 1/5 are REALLY first/last.
        `function` is the function you want to be called.  Arguments vary by
        hook.
        """

        return []

    def links(self):
        """Returns a default hierarchy of links, represented as a tree of
        PluginLink objects.
        """

        return []

    def widgets(self):
        """Returns a list of tuples in the form `(widget_name, priority, template_path)`.

        A widget is similar to a hook, except it's a Mako template rather than
        a Python function.

        `widget_name` is a string identifying a template hook somewhere in
        either Spline core or another plugin.
        `priority` is a number from 1 to 5 using Apache conventions: 3 is
        normal, 2/4 are first/last, 1/5 are REALLY first/last.
        `template_path` is the path to a template containing this widget.
        Arguments vary by hook.
        """

        return []


class LocalPlugin(PluginBase):
    """A pseudo-plugin created from an instance directory.  It examines the
    directory for appropriately-named subdirectories containing static data and
    returns them from the appropriate methods.
    """

    def __init__(self, root_dir):
        """This can't call super() as it changes the signature.  Whatever."""
        self.root_dir = root_dir

    def controllers(self):
        """Instances probably shouldn't be running new code; that should be in
        a real plugin.  Also, the namespace would be all wrong.
        """
        # TODO make this possible somehow in a controllers/ dir?
        return {}

    def template_dirs(self):
        return [
            (os.path.join(self.root_dir, 'templates'), 1)
        ]

    def static_dir(self):
        """Assumed to be a directory named `public`."""
        return os.path.join(self.root_dir, 'public')

    def model(self):
        """No way!"""
        return []

    def hooks(self):
        """Not yet.

        More reasonable than entire controllers; they could be put in a special
        hooks.py file and loaded/inspected by this class.
        """
        return []

    def links(self):
        """Also not yet.

        Needed, someday.  Possibly a special file just like above.  I don't
        know.  We might need to load an entire real file, scrap all this
        nonsense, and make the base class do some reasonable introspection
        regardless of whether this is a plugin or instance.
        """

        return []

    def widgets(self):
        """The contents of a `widgets` directory become widgets.  Files are
        associated with the widget hook matching the filename.  Subdirectories'
        contents are all associated with the widget hook matching the name of
        the subdirectory.
        """

        widget_files = []
        # XXX This sucks and is going to lead to so many fucking collisions
        widget_dir = os.path.join(self.root_dir, 'templates', 'widgets')
        if not os.path.isdir(widget_dir):
            # Directory missing or bogus; no widgets
            return []

        widgets = []
        for candidate_file in os.listdir(widget_dir):
            candidate_path = os.path.join(widget_dir, candidate_file)
            if os.path.isdir(candidate_path):
                # Directory: add every file inside
                for widget_file in os.listdir(candidate_path):
                    widget_path = os.path.join(candidate_path, widget_file)
                    if os.path.isfile(widget_path):
                        basename, whatever = os.path.splitext(widget_file)
                        widgets.append( (
                            candidate_file,
                            3,
                            '/widgets/%s/%s' % (candidate_file, widget_file)
                        ) )
            else:
                # Single file
                widget, whatever = os.path.splitext(widget_file)
                widgets.append( (widget, 3, '/widgets/%s' % candidate_file) )

        return widgets
