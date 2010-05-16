from pkg_resources import iter_entry_points

from mako.lookup import TemplateLookup
from mako.template import Template
from pylons.util import PylonsInstaller

class Installer(PylonsInstaller):
    """Overrides the default Pylons/Paste installation mechanism.

    This stitches together configuration templates from all known spline
    plugins.
    """

    def description(self, config):
        return 'Spline'

    def template_renderer(self, content, vars, filename=None):
        """Renders the passed-in template.

        `spline_plugin_config_files` is set to a list of paths to plugin
        configuration templates.
        """
        plugin_config_files = []
        for ep in iter_entry_points('spline.plugins'):
            plugin_class = ep.load()
            plugin = plugin_class(ep)

            config_path = plugin.config_template_path()
            if config_path:
                plugin_config_files.append(config_path)

        lookup = TemplateLookup(directories=['/'])
        tmpl = Template(content, lookup=lookup)
        return tmpl.render_unicode(
            spline_plugin_config_files=plugin_config_files,
            **vars
        ).encode('utf8')
