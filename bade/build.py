from __future__ import unicode_literals
import datetime
import os
import multiprocessing
import shutil
import subprocess

from docutils.core import publish_parts as docutils_publish
from mako import exceptions as mako_exceptions

from . import utils, config


class Build(object):

    def __init__(self, config):
        'Create config, build blog tree'
        self.config = config
        self.postpaths = self._postpaths()
        self.index = index.BadeIndex(config)

    def clean(self):
        'Carelessly wipe out the build dir'
        shutil.rmtree(self.config.build, ignore_errors=True)

    def render_err(self, name, context):
        'Render a template, with some debugging'
        template = self.config.template_lookup.get_template(name)
        try:
            return template.render(**context), None
        except:
            if self.config.debug:
                error_html = (mako_exceptions.html_error_template()
                                             .render(full=False)
                                             .decode('utf-8'))
                return error_html, True
            raise

    def write_html(self, template, context, buildpath):
        html, err = self.render_err(template, context)
        htmldir = os.path.dirname(buildpath)
        if not os.path.exists(htmldir) and htmldir:
            os.makedirs(htmldir)
        with open(buildpath, 'w') as htmlfile:
            htmlfile.write(html)
        if err:
            print("Debug HTML written to: {0}".format(buildpath))
        else:
            print("Writing to: {0}".format(buildpath))


    def commit_github(self, rst_path):
        'Return the lastest commit and GitHub link for a given path'
        try:
            github_url = os.path.join(self.config.github,
                                      'blob',
                                      'master',
                                      rst_path)
        except AttributeError:
            github_url = '#'
        git_cmd = ['git', 'log', '-n', '1',
                   '--pretty=format:%h', '--', rst_path]
        try:
            commit = subprocess.check_output(git_cmd).decode('utf-8')
        except subprocess.CalledProcessError:
            commit = 'HEAD'
        return commit, github_url

    def page(self, rst_path):
        'Build a page'
        context, buildpath = self.index.page_context(rst_path)
        context['content_html'] = utils.render_rst(rst_path)
        self.write_html('page.html', context, buildpath)

    def post(self, rst_path):
        'Build a page'
        render_context, buildpath = self.index.post_context(rst_path)
        render_context['content_html'] = utils.render_rst(rst_path)
        self.write_html('post.html', render_context, buildpath)

    def blog_page(self):
        blogtree_rst = self.config.blogtree_rst
        buildpath = (os.path.join(self.config.build, blogtree_rst)
                            .replace('rst', 'html'))
        index_rst, _ = self.render_err(blogtree_rst,
                                       self.index.page_context(blogtree_rst))
        content_html = docutils_publish(index_rst, writer_name='html')
        context = self.index.context()
        context.update({
            'page_title': self.config.blogname,
            'content_html': content_html['html_body'],
        })
        return self.write_html('page.html', context, buildpath)

    def index_html(self):
        'Build the site index'
        index_template = self.config.index_template
        render_context, _ = self.index.page_context()
        self.write_html(index_template, render_context,
                        os.path.join(self.config.build, 'index.html'))

    def pages(self, pool):
        pool.map_async(self.page, self.config.pages)

    def posts(self, pool):
        pool.map_async(self.post, self.postpaths)

    def copy_assetpaths(self):
        'Copy everything specified in the config to the build directory'
        for source in self.config.assetpaths:
            destination = os.path.join(self.config.build, source)
            if os.path.isdir(source):
                shutil.rmtree(destination)
                shutil.copytree(source, destination)
            if os.path.isfile(source):
                shutil.copy(source, destination)

    def sass(self):
        try:
            sources = self.config.sassin,
            destination = os.path.join(self.config.build, self.config.sassout)
        except AttributeError as exc:
            if 'not configured' in str(exc):
                return
        try:
            import sass_cli  # NOQA
        except ImportError:
            message = 'Sass input configured, but `sass_cli` not installed'
            raise ImportError(message)
        for source in sources:
            subprocess.check_call(['sass', source, destination])

    def run(self):
        'Call all the methods to render all the things'
        pool = multiprocessing.Pool(multiprocessing.cpu_count())
        if self.config.debug:
            pass
        pool.map_async = lambda fn, *it: list(map(fn, *it))
        self.copy_assetpaths()
        self.sass()
        self.pages(pool)
        self.posts(pool)
        self.blog_page()
        self.index_html()
        pool.close()
        pool.join()
