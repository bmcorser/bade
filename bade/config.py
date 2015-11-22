from docutils.parsers.rst import directives
from docutils.parsers.rst import roles

from .directives import (
    pygments_directive,
    dotgraph_directive,
    eqtexsvg_directive,
    eqtexsvg_role,
)


class Configuration(object):
    'Holds the defaults for a Build'

    _defaults = {
        'assetpaths': ['assets'],
        'blogroot': 'blog',
        'cache_dir': '.bade-cache',
        'blogtree_rst': 'blog.rst',
        'blogtitle': 'Blog',
        'build': '_build',
        'debug': False,
        'dotgraph_directive': True,
        'index_template': 'index.html',
        'pages': [],
        'pygments_directive': True,
        'eqtexsvg_directive': True,
        'template_dirs': ['templates'],
    }

    def __init__(self, config_dict, overrides=None):
        'Handle mapping a dict to required configuration parameters'
        if overrides is None:
            overrides = dict()
        self._overrides = overrides
        self._config_dict = config_dict
        if self.pygments_directive:
            # Render code blocks using pygments
            directives.register_directive('code-block', pygments_directive)
        if self.dotgraph_directive:
            # Render DOT to SVG
            directives.register_directive('dot-graph', dotgraph_directive)
        if self.eqtexsvg_directive:
            # Render LaTeX to SVG
            directives.register_directive('maths', eqtexsvg_directive)
            roles.register_canonical_role('maths', eqtexsvg_role)
        if not isinstance(self.template_dirs, list):
            raise TypeError('Misconfigured: `template_dirs` should be a list')
        if not isinstance(self.pages, list):
            raise TypeError('Misconfigured: `pages` should be a list')

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

    def setval(self, name, value):
        'Set a configuration value'
        self._config_dict[name] = value
