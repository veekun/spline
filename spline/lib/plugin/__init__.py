"""Functionality generally needed to build a plugin."""
import os.path

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
