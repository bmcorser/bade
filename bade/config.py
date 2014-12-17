import os
from os import environ
from docutils.parsers.rst import directives
from mako import lookup, exceptions

from .directives import pygments_directive, DotgraphDirective


class Configuration(object):
    'Holds the defaults for a Build'

    _defaults = {
        'assetpaths': [],
        'blogroot': 'blog',
        'blogtree_rst': 'blog.rst',
        'build': '_build',
        'debug': False,
        'dotgraph_directive': True,
        'index_template': 'index.html',
        'pages': [],
        'pygments_directive': True,
        'template_dirs': ['templates'],
    }

    def __init__(self, config_dict, overrides=None):
        'Handle mapping a dict to required configuration parameters'
        if overrides is None:
            overrides = dict()
        self._config_dict = config_dict
        self._overrides = overrides
        if self.pygments_directive:
            # Render code blocks using pygments
            directives.register_directive('code-block', pygments_directive)
        if self.pygments_directive:
            # Render DOT to SVG
            directives.register_directive('dot-graph', DotgraphDirective)
        self._config_dict['pages'] = ["{0}.rst".format(path)
                                      for path in config_dict.get('pages', [])]
        package_templates = os.path.join(environ.get('VIRTUAL_ENV'),
                                         'bade/templates')
        if not isinstance(self.template_dirs, list):
            raise TypeError('Misconfigured: `template_dirs` should be a list')
        if not isinstance(self.pages, list):
            raise TypeError('Misconfigured: `pages` should be a list')
        self._template_lookup = lookup.TemplateLookup(
            directories=self.template_dirs
        )
        self._default_template_lookup = lookup.TemplateLookup(
            directories=[package_templates]
        )

    def __getattr__(self, name):
        'Refer to overrides, passed config or defaults'
        try:
            return self._overrides[name]
        except KeyError:
            try:
                return self._config_dict[name]
            except KeyError:
                try:
                    return self._defaults[name]
                except KeyError:
                    raise AttributeError("'{0}' not configured".format(name))

    def get_template(self, name):
        'Lookup a template from either packaged templates or configured path'
        try:
            template = self._template_lookup.get_template(name)
        except exceptions.TopLevelLookupException:
            template = self._default_template_lookup.get_template(name)
        return template

    def setval(self, name, value):
        'Set a configuration value'
        self._config_dict[name] = value
