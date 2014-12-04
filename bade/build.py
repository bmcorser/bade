from __future__ import unicode_literals
import datetime
import os
import multiprocessing
import shutil
import subprocess

from docutils.core import publish_parts as docutils_publish
from mako.template import Template

from . import utils



shutil.rmtree('_build', ignore_errors=True)

def write_html(html, htmlpath):
    htmldir = os.path.dirname(htmlpath)
    if not os.path.exists(htmldir):
        os.makedirs(htmldir)
    with open(htmlpath, 'w') as htmlfile:
        htmlfile.write(html.encode('utf8'))




def render_rst(rst_path):
    with open(rst_path, 'r') as rst_file:
        rst_string = rst_file.read()
    return docutils_publish(rst_string, writer_name='html')['html_body']




def build_blog_page(blog_template):
    buildpath = blog_template.replace('templates', '_build')
    context = {
        'index': index,
        'meta': {'title': 'Chatter'},
    }
    template = Template(filename=blog_template, lookup=template_lookup)
    write_html(template.render(**context), buildpath)


def build_copy_dir(dir_):
    shutil.copytree(dir_, os.path.join('_build', dir_))

def build_copy_file(source, dest):
    shutil.copy(source, dest)



class Build(object):

    def __init__(self, config):
        self.config = config
        find_posts = ['find', self.config.blogroot, '-name', '*.rst']
        self.posts = sorted(subprocess.check_output(find_posts).split(),
                            reverse=True)
        self.indexes = self._indexes()

    def title_buildpath(self, root, rst_path):
        bare_path, ext = os.path.splitext(rst_path)
        slug = os.path.split(bare_path)[-1]
        title = ' '.join(slug.split('-')).capitalize()
        buildpath = (bare_path + '.html').replace(root or self.config.blogroot,
                                                  self.config.build)
        return title, buildpath

    def parse_meta(self, rst_path):
        title, buildpath = self.title_buildpath(None, rst_path)
        return {
            'title': title,
            'buildpath': buildpath,
        }

    def _indexes(self):
        D = utils.OrderedDefaultdict
        month_tree = D(lambda: D(list))
        for rst_path in self.posts:
            meta = self.parse_meta(rst_path)
            date = datetime.date(*map(int, rst_path.split(os.sep)[1:4]))
            meta['date'] = date
            month_tree[date.year][date.month].append(meta)
        return month_tree

    def build_page(self, rst_path):
        title, buildpath = self.title_buildpath(os.path.dirname(rst_path),
                                                rst_path)
        context = {
            'index': self.index,
            'title': title,
            'content_html': render_rst(rst_path),
        }
        template = Template(filename='templates/page.html',
                            lookup=self.config.template_lookup)
        write_html(template.render(**context), buildpath)

    def iter_posts(self, rst_path, direction):
        post_index = self.posts.index(rst_path)
        iter_to = post_index + direction
        if iter_to < 0:
            return None
        if iter_to == len(self.posts):
            return None
        return self.parse_meta(self.posts[iter_to])

    def build_post(self, rst_path):
        context = {
            'next_post': self.iter_posts(rst_path, -1),
            'previous_post': self.iter_posts(rst_path, +1),
            'indexes': self.indexes,
            'meta': self.parse_meta(rst_path),
            'content_html': render_rst(rst_path),
        }
        template = Template(filename='templates/post.html', lookup=template_lookup)
        write_html(template.render(**context), context['meta']['buildpath'])


    def run():

        pool = multiprocessing.Pool(8)
        map(build_page, (
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
