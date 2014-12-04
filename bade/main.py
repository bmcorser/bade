from __future__ import unicode_literals
import collections
import datetime
import os
import multiprocessing
import shutil
import subprocess

from docutils.core import publish_parts as docutils_publish
from docutils.parsers.rst import directives
from pygments_directive import pygments_directive
from mako.template import Template
from mako.lookup import TemplateLookup

class OrderedDefaultdict(collections.OrderedDict):

    def __init__(self, *args, **kwargs):
        if not args:
            self.default_factory = None
        else:
            if not (args[0] is None or callable(args[0])):
                raise TypeError('first argument must be callable or None')
            self.default_factory = args[0]
            args = args[1:]
        super(OrderedDefaultdict, self).__init__(*args, **kwargs)

    def __missing__(self, key):
        if self.default_factory is None:
            raise KeyError(key)
        self[key] = default = self.default_factory()
        return default

    def __reduce__(self):  # optional, for pickle support
        args = (self.default_factory,) if self.default_factory else ()
        return self.__class__, args, None, None, self.iteritems()

directives.register_directive('code-block', pygments_directive)

shutil.rmtree('_build', ignore_errors=True)

def write_html(html, htmlpath):
    htmldir = os.path.dirname(htmlpath)
    if not os.path.exists(htmldir):
        os.makedirs(htmldir)
    with open(htmlpath, 'w') as htmlfile:
        htmlfile.write(html.encode('utf8'))


def parse_meta(rst_path):
    bare_path, ext = os.path.splitext(rst_path)
    slug = os.path.split(bare_path)[-1]
    buildpath = (bare_path + '.html').replace('blog', '_build')
    return {
        'date': datetime.date(*map(int, rst_path.split(os.sep)[1:4])),
        'title': ' '.join(slug.split('-')).capitalize(),
        'slug': slug,
        'buildpath': buildpath,
    }


def render_rst(rst_path):
    with open(rst_path, 'r') as rst_file:
        rst_string = rst_file.read()
    return docutils_publish(rst_string, writer_name='html')['html_body']


def build_index(rst_paths):
    D = OrderedDefaultdict
    month_tree = D(lambda: D(list))
    for rst_path in rst_paths:
        meta = parse_meta(rst_path)
        date = meta['date']
        month_tree[date.year][date.month].append(meta)
    return month_tree


def render_mako(rst_path):
    context = {
        'index': index,
        'meta': parse_meta(rst_path),
        'content_html': render_rst(rst_path),
    }
    template = Template(filename='templates/post.html', lookup=template_lookup)
    write_html(template.render(**context), context['meta']['buildpath'])

def build_blog_page(blog_template):
    buildpath = blog_template.replace('templates', '_build')
    context = {
        'index': index,
        'meta': {'title': 'Chatter'},
    }
    template = Template(filename=blog_template, lookup=template_lookup)
    write_html(template.render(**context), buildpath)

def build_page(rst_path):
    bare_path, ext = os.path.splitext(rst_path)
    slug = os.path.split(bare_path)[-1]
    buildpath = (bare_path + '.html').replace('pages', '_build')
    context = {
        'index': index,
        'meta': {
            'title': slug.capitalize(),
            'buildpath': buildpath,
        },
        'content_html': render_rst(rst_path),
    }
    template = Template(filename='templates/page.html', lookup=template_lookup)
    write_html(template.render(**context), context['meta']['buildpath'])

def build_copy_dir(dir_):
    shutil.copytree(dir_, os.path.join('_build', dir_))

def build_copy_file(source, dest):
    shutil.copy(source, dest)

def build():
    global index
    global template_lookup

    find = ['find', 'blog', '-name', '*.rst']
    rst_paths = sorted(subprocess.check_output(find).split(), reverse=True)

    index = build_index(rst_paths)
    template_lookup = TemplateLookup(directories=['.'])

    pool = multiprocessing.Pool(8)
    pool.map_async(build_page, (
        'pages/bio.rst',
        'pages/projects.rst',
    ))
    pool.map_async(render_mako, rst_paths)
    pool.map_async(build_copy_dir, (
        'assets/images',
        'assets/js',
        'assets/fonts',
        'bower_components',
    ))
    pool.apply_async(shutil.copy, ('templates/index.html', '_build'))
    subprocess.check_call(['sass', 'assets/scss', '_build/assets/css'])
    build_blog_page('templates/blog.html')

    pool.close()
    pool.join()
    print('done.')


if __name__ == '__main__':
    build()
