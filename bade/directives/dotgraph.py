import tempfile
from docutils import nodes
import pydot
from bs4 import BeautifulSoup


def dotgraph_directive(name, arguments, options, content, *args):

    graph = pydot.dot_parser.parse_dot_data('\n'.join(content))[0]
    tmp = tempfile.NamedTemporaryFile()
    print("Graph temp: {0}".format(tmp.name))
    graph[0].write_svg(tmp.name)
    svg = BeautifulSoup(tmp.read().decode('utf8'), 'html.parser')
    svg.find('svg').attrs['class'] = 'dot-graph'
    return [nodes.raw('', str(svg), format='html')]

dotgraph_directive.arguments = (0, 0, 1)
dotgraph_directive.content = 1
