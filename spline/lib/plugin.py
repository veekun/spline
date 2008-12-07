class PluginBase(object):
    """Base object for spline plugins.  Plugins should advertise a subclass of
    this class as an entry point.
    """

    def __init__(self):
        pass

    def controllers(self):
        """Returns a dictionary mapping routing names to controllers."""
        return {}
