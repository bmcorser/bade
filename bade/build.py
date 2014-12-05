from __future__ import unicode_literals
import datetime
import os
import multiprocessing
import shutil
import subprocess

from docutils.core import publish_parts as docutils_publish
from mako.template import Template

from . import utils


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





class Build(object):

    def __init__(self, config):
        'Create config, build blog tree'
        self.config = config
        self.blogtree = self._blogtree()

    def clean(self):
        'Carelessly wipe out the build dir'
        shutil.rmtree(self.config.build, ignore_errors=True)

    def build_copy_dir(self, dir_):
        shutil.copytree(dir_, os.path.join(self.config.build, dir_))

    def build_copy_file(self, source, dest):
        shutil.copy(source, dest)

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

    def _blogtree(self):
        find = ['find', self.config.blogroot, '-name', '*.rst']
        self.posts = sorted(subprocess.check_output(find).split(),
                            reverse=True)
        D = utils.OrderedDefaultdict
        blogtree = D(lambda: D(list))
        for rst_path in self.posts:
            meta = self.parse_meta(rst_path)
            date = datetime.date(*map(int, rst_path.split(os.sep)[1:4]))
            meta['date'] = date
            blogtree[date.year][date.month].append(meta)
        return blogtree

    def build_page(self, rst_path):
        title, buildpath = self.title_buildpath(os.path.dirname(rst_path),
                                                rst_path)
        context = {
            'index': self.blogtree,
            'title': title,
            'content_html': render_rst(rst_path),
        }
        template = Template(filename='page.html',
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
        print("Building {0}".format(rst_path))
        context = {
            'next_post': self.iter_posts(rst_path, -1),
            'previous_post': self.iter_posts(rst_path, +1),
            'blogtree': self.blogtree,
            'meta': self.parse_meta(rst_path),
            'content_html': render_rst(rst_path),
        }
        template = Template(filename='post.html', lookup=template_lookup)
        write_html(template.render(**context), context['meta']['buildpath'])

    def build_pages(self, pool):
        pool.map_async(self.build_page, self.config.pages)

    def build_posts(self, pool):
        pool.map_async(self.build_post, self.posts)

    def process_sass(self):
        subprocess.check_call(['sass', self.config.sasspath, '_build/assets/css'])

    def run(self):
        pool = multiprocessing.Pool(multiprocessing.cpu_count())
        if self.config.debug:
            pool.map_async = map
        self.build_pages(pool)
        self.build_posts(pool)
        exit()
        pool.map_async(self.build_copy_dir, self.config.assetpaths)
        pool.apply_async(shutil.copy, ('index.html', '_build'))
        build_blog_page('blog.html')

        pool.close()
        pool.join()
        print('done.')
