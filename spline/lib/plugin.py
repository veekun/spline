class PluginBase(object):
    """Base object for spline plugins.  Plugins should advertise a subclass of
    this class as an entry point.
    """

    def __init__(self):
        pass

    def controllers(self):
        """Returns a dictionary mapping routing names to controllers."""
        return {}

    def model(self):
        """Returns a list of classes to stick in Spline's model namespace.

        Please be sure to list ALL model classes here; otherwise, the rest of
        the app will have trouble finding them, which can be important for
        things like creating all new tables as InnoDB.
        """
        return []
