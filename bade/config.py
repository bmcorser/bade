from docutils.parsers.rst import directives
from mako.lookup import TemplateLookup

from . import utils


class Configuration(object):
    'Holds the defaults for a Build'

    defaults = {
        'pygments_directive': True,
        'build': '_build',
        'template_dirs': ['templates'],
        'blogroot': 'blog',
        'pages': [],
        'debug': True,
    }

    def __init__(self, config_dict, overrides={}):
        'Handle mapping a dict to required configuration parameters'
        self.config_dict = config_dict
        self.overrides = overrides
        if self.pygments_directive:
            # Render code clocks using pygments
            directives.register_directive('code-block',
                                          utils.pygments_directive)
        if not isinstance(self.template_dirs, list):
            raise TypeError('Misconfigured: `template_dirs` should be a list')
        if not isinstance(self.pages, list):
            raise TypeError('Misconfigured: `pages` should be a list')
        self.config_dict['pages'] = ["{0}.rst".format(path)
                                     for path in config_dict['pages']]
        self.template_lookup = TemplateLookup(directories=self.template_dirs)

    def __getattr__(self, name):
        try:
            return self.overrides[name]
        except KeyError:
            try:
                return self.config_dict[name]
            except KeyError:
                return self.defaults[name]

    def setval(self, name, value):
        'Set a configuration value'
        self.config_dict[name] = value
