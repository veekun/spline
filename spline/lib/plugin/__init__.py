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

        `hook_name` is a string identifying a hook somewhere in either Spline
        core or another plugin.
        `priority` is a number from 1 to 5 using Apache conventions: 3 is
        normal, 2/4 are first/last, 1/5 are REALLY first/last.
        `function` is the function you want to be called.  Arguments vary by
        hook.
        """

        return []


class InstancePlugin(PluginBase):
    """A pseudo-plugin created from an instance directory.  It examines the
    instance dir for appropriately-named subdirectories containing static
    data and returns them from the appropriate methods.
    """

    # TODO that 'examine' bit could stand to be true

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
