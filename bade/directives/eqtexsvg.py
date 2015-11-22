import subprocess
import tempfile
from docutils import nodes
from bs4 import BeautifulSoup

def eqtexsvg(tex, cls_name):
    tmp = tempfile.NamedTemporaryFile()
    print("LaTeX temp: {0}".format(tmp.name))
    subprocess.check_call(['eqtexsvg', '-f', tex, '-o', tmp.name])
    svg = BeautifulSoup(tmp.read().decode('utf8'), 'html.parser')
    svg.find('svg').attrs['class'] = cls_name
    return str(svg)

def eqtexsvg_directive(name, arguments, options, content, *args):
    joined_content = '\n'.join(content)
    svg = eqtexsvg(joined_content, 'maths-eqtexsvg')
    return [nodes.raw('', svg, format='html')]
eqtexsvg_directive.arguments = (0, 0, 1)
eqtexsvg_directive.content = 1

def eqtexsvg_role(name, rawtext, text, lineno, inliner, options={}, content=[]):
    stripped_raw = "${0}$".format(rawtext.replace(':maths:`', '')[:-1])
    svg = eqtexsvg(stripped_raw, 'maths-eqtexsvg-inline')
    return [nodes.raw('', svg, format='html')], []
