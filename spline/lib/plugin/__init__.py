"""Functionality generally needed to build a plugin."""

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
        """Returns a list of directories containing templates."""
        return []

    def model(self):
        """Returns a list of classes to stick in Spline's model namespace.

        Please be sure to list ALL model classes here; otherwise, the rest of
        the app will have trouble finding them, which can be important for
        things like creating all new tables as InnoDB.
        """
        return []

    def hooks(self):
        """Returns a list of tuples in the form `(hook_name, priority, function)`.

        `hook_name` is a string identifying a hook somewhere in either Spline
        core or another plugin.
        `priority` is a number from 1 to 5 using Apache conventions: 3 is
        normal, 2/4 are first/last, 1/5 are REALLY first/last.
        `function` is the function you want to be called.  Arguments vary by
        hook.
        """

        return []
