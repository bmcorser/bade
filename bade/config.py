from docutils.parsers.rst import directives
from mako.lookup import TemplateLookup

from . import utils


class Configuration(object):

    defaults = {
        'pygments_directive': True,
        'build': '_build',
        'blogroot': 'blog',
        'pages': [],
    }

    def __init__(self, config_dict, overrides=dict()):
        template_dirs = config_dict.pop('template_dirs', ['templates'])
        if not isinstance(template_dirs, list):
            raise TypeError('Misconfigured: `templates` should be a list')
        self.template_lookup = TemplateLookup(directories=template_dirs)
        self.config_dict = config_dict
        self.overrides = overrides
        if self.pygments_directive:
            # Render code clocks using pygments
            directives.register_directive('code-block',
                                          utils.pygments_directive)

    def __getattr__(self, name):
        try:
            return self.overrides[name]
        except KeyError:
            try:
                return self.config_dict[name]
            except KeyError:
                return self.defaults[name]
