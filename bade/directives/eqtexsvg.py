import hashlib
import os
import subprocess
import tempfile
from docutils import nodes
from bs4 import BeautifulSoup

CACHE_DIR = None


def _cache_path(data):
    if not CACHE_DIR:
        return
    key = hashlib.sha1(data).hexdigest()
    return os.path.join(CACHE_DIR, key)


def _cache_get(path):
    if os.path.isfile(path):
        with open(path, 'r') as cache_file:
            data = cache_file.read()
            if data:
                return data
            return


def _cache_set(path, data):
    if not CACHE_DIR:
        return
    with open(path, 'w') as cache_file:
        cache_file.write(data)


def eqtexsvg(tex, cls_name):
    cache_path = _cache_path(tex.encode('utf8'))
    cached = _cache_get(cache_path)
    if cached:
        return cached
    tmp = tempfile.NamedTemporaryFile()
    print("LaTeX temp: {0}".format(tmp.name))
    subprocess.check_call(['eqtexsvg', '-f', tex, '-o', tmp.name])
    svg = BeautifulSoup(tmp.read().decode('utf8'), 'html.parser')
    svg.find('svg').attrs['class'] = cls_name
    svg_str = str(svg)
    _cache_set(cache_path, svg_str)
    return svg_str


def eqtexsvg_directive(name, arguments, options, content, *args):
    joined_content = '\n'.join(content)
    svg = eqtexsvg(joined_content, 'maths-eqtexsvg')
    return [nodes.raw('', svg, format='html')]
eqtexsvg_directive.arguments = (0, 0, 1)
eqtexsvg_directive.content = 1


def eqtexsvg_role(
        name, rawtext, text, lineno, inliner, options={}, content=[]):
    stripped_raw = "${0}$".format(rawtext.replace(':maths:`', '')[:-1])
    svg = eqtexsvg(stripped_raw, 'maths-eqtexsvg-inline')
    return [nodes.raw('', svg, format='html')], []
