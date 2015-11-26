import hashlib
import os
import subprocess
import tempfile
from docutils import nodes
import bs4

CACHE_DIR = None
TEMPLATE = '''
\\documentclass[varwidth,border=0.5pt]{standalone}
\\usepackage{standalone}
\\usepackage{amsmath}
\\usepackage{amssymb}
\\usepackage{amsfonts}
\\usepackage{mathtools}
\\begin{document}
%s
\\end{document}
'''

def run(cmd):
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = proc.communicate()
    if proc.returncode > 0:
        exit(stdout)
    return stdout, stderr


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
    workspace = tempfile.mkdtemp()
    print("LaTeX temp: {0}".format(workspace))
    tex_path = os.path.join(workspace, 'eqn.tex')
    dvi_path = os.path.join(workspace, 'eqn.dvi')
    with open(tex_path, 'w') as tex_file:
        tex_file.write((TEMPLATE % tex))
    run(['latex', '-output-directory=%s' % workspace, tex_path])
    svg_bytes, _ = run(['dvisvgm', '-v0', '-a', '-n', '-s', '-e', dvi_path])
    svg = bs4.BeautifulSoup(svg_bytes.decode('utf8'), 'html.parser')
    svg.find('svg').attrs['class'] = cls_name
    svg.find('svg').attrs['style'] = 'overflow: visible'
    for element in svg:
        if isinstance(element, bs4.element.ProcessingInstruction):
            element.extract()
            break
    svg_str = str(svg).strip()
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
