"""Functionality used by Spline core to load and otherwise manipulate plugins.
Plugins themselves should never need to touch anything in this module!
"""

from pkg_resources import iter_entry_points

from pylons import config

import spline.model

def load_plugins(paths, extra_plugins={}):
    """Loads all available plugins and sticks the configuration they offer into
    `spline.plugins.*` keys in the given config dictionary.

    `paths` is the Pylons setup path dictionary; we need this to be able to add
    to search paths, but this function must be called after the app is setup.

    `extra_plugins` is an optional dict of previously-instantiated plugin
    objects that will be loaded after the others, with the keys as the plugin
    names.
    """

    plugins = {}          # plugin_name => plugin
    controllers = {}      # controller_name => controller
    template_tuples = []  # (directory, priority)
    static_dirs = {}      # directories
    hooks = {}            # hook_name => { priority => [functions] }

    plugins.update(extra_plugins)

    for ep in iter_entry_points('spline.plugins'):
        plugin_class = ep.load()

        if ep.name[0:7] == 'spline':
            raise ValueError("Plugin names beginning with 'spline' are reserved.")

        plugin = plugin_class()
        plugins[ep.name] = plugin

    for plugin_name, plugin in plugins.items():
        # Get list of controllers
        for name, cls in plugin.controllers().iteritems():
            controllers[name] = cls

        # Get lists of dirs and add them to the appropriate lookup list
        template_tuples.extend(plugin.template_dirs())

        static_dir = plugin.static_dir()
        if static_dir is not None:
            static_dirs[plugin_name] = static_dir

        # Get list of model classes and inject them into model module
        for cls in plugin.model():
            setattr(spline.model, cls.__name__, cls)

        # Register some hooks
        for name, priority, function in plugin.hooks():
            if not name in hooks:
                hooks[name] = {}
            if not priority in hooks[name]:
                hooks[name][priority] = []

            hooks[name][priority].append(function)

    # Spline builtin templates have normal priority: 3
    for directory in paths['templates']:
        template_tuples.append((directory, 3))
    # Extract the list of template directories in order, remembering that lower
    # numbers mean higher priority, and we want higher priority directories to
    # be earlier in the array so they are seen first
    template_tuples.sort(key=lambda x: x[1])
    template_dirs = [x[0] for x in template_tuples]

    config['spline.plugins'] = plugins
    config['spline.plugins.controllers'] = controllers
    config['spline.plugins.hooks'] = hooks
    config['spline.plugins.template_directories'] = template_dirs

    paths['templates'] = template_dirs  # already includes defaults
    paths['static_files'].update(static_dirs)

# Arg name is designed to be unlikely to collide with any arbitrary kwarg
def run_hooks(_spline_hook_name, *args, **kwargs):
    """Runs the hooks registered for the given name, in priority order, passing
    along all other arguments.

    Current hooks:
    before_controller   immediately before any controller is run
    after_setup         immediately following the Pylons environment setup
    routes_mapping      near the end of Routes mapping, just before default
                        routes are defined
    """

    all_hooks = config['spline.plugins.hooks']

    if not _spline_hook_name in all_hooks:
        # No hooks; bail
        return
    hooks = all_hooks[_spline_hook_name]

    for priority in [1, 2, 3, 4, 5]:
        if not priority in hooks:
            # Nothing for this priority; bail
            continue

        for function in hooks[priority]:
            function(*args, **kwargs)

    return

