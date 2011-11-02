"""Functionality generally needed to build a plugin."""
from collections import namedtuple
import os.path

from pkg_resources import resource_exists, resource_filename, resource_isdir

from spline.i18n import NullTranslator

class Priority(object):
    """Enum for the order in which to load various components."""
    VERY_FIRST  = 1
    FIRST       = 2
    NORMAL      = 3
    LAST        = 4
    VERY_LAST   = 5

class PluginLink(object):
    """Represents a link in a plugin."""

    def __init__(self, label, url=None, children=[], collapsed=False, translator_class=NullTranslator, i18n_context=None):
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

        `translator`
            A class used to translate the label. Will be instantiated.

        `i18n_context`
            I18n context, passed to the translator
        """

        self.label = label
        self.url = url
        self.children = children
        self.collapsed = collapsed
        self.translator_class = translator_class
        self.i18n_context = i18n_context

        # Make this tree bidirectional
        self.parent = None
        for child in children:
            child.parent = self


class PluginBase(object):
    """Base object for spline plugins.  Plugins should advertise a subclass of
    this class as an entry point.
    """

    config_template_filename = 'deployment.ini_tmpl'

    def _resource_or_bust(self, path, isdir=False):
        """Returns the path to a resource, or None if it doesn't exist."""
        if resource_exists(self.module_name, path) and \
           resource_isdir(self.module_name, path) == isdir:
            return resource_filename(self.module_name, path)

        return None


    def __init__(self, entry_point):
        self.entry_point = entry_point

    @property
    def module_name(self):
        """This plugin's module name, e.g. 'splinext.pokedex'."""
        return self.entry_point.module_name

    def config_template_path(self):
        """Returns a path to a Mako template for a new configuration file.
        This file will be included in configuration files created by `paster
        make-config`.

        By default, looks for a `deployment.ini_tmpl` file in the base module
        directory.
        """
        return self._resource_or_bust(self.config_template_filename)

    def controllers(self):
        """Returns a dictionary mapping routing names to controllers."""
        return {}

    def template_dirs(self):
        """Returns a list of directories containing templates.

        Each element of this list should be a tuple of (directory, priority).

        By default, looks for a `templates` directory in the base module
        directory, and assumes normal priority.
        """
        template_dir = self._resource_or_bust('templates', isdir=True)
        if template_dir:
            return [ (template_dir, Priority.NORMAL) ]
        else:
            return []

    def static_dir(self):
        """Returns a directory containing static files, or None for none.

        By default, looks for a `public` directory in the base module
        directory.
        """
        return self._resource_or_bust('public', isdir=True)

    def content_dir(self):
        """Returns a directory containing content files, or None for none.

        By default, looks for a `content` directory in the base module
        directory.
        """
        return self._resource_or_bust('content', isdir=True)

    def hooks(self):
        """Returns a list of tuples in the form `(hook_name, priority, function)`.

        A hook is a named point within Python code that allows plugins to
        inject their own code; for example, there is a `before_controller` hook
        that plugins can use to execute code before each controller call.  The
        `users` plugin uses this to check the session for a logged-in user on
        each request.

        `hook_name`
            A string identifying a hook somewhere in either Spline core or
            another plugin.

        `priority`
            A `Priority`, identifying when this hook should be run.

        `function`
            The function you want to be called.  Arguments vary by hook.
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

        `widget_name`
            A string identifying a template hook somewhere in either Spline
            core or another plugin.

        `priority`
            A `Priority`, identifying when this hook should be run.

        `template_path`
            The path to a template containing this widget.  Arguments vary by
            hook.
        """

        return []


class LocalPlugin(object):
    """A pseudo-plugin created from an instance directory.  It examines the
    directory for appropriately-named subdirectories containing static data and
    returns them from the appropriate methods.
    """

    def __init__(self, root_dir):
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

    def content_dir(self):
        """Assumed to be a directory named `content`."""
        return os.path.join(self.root_dir, 'content')

    def model(self):
        """No way!"""
        return []

    def hooks(self):
        """Can be overridden in plugin.py."""

        return []

    def links(self):
        """Can be overridden in plugin.py."""

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
                widget, whatever = os.path.splitext(candidate_file)
                widgets.append( (widget, 3, '/widgets/%s' % candidate_file) )

        return widgets
