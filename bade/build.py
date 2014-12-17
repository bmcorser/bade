from __future__ import unicode_literals
import datetime
import os
import multiprocessing
import shutil
import subprocess

from docutils.core import publish_parts as docutils_publish
from mako import exceptions as mako_exceptions

from . import utils


def render_rst(rst_path):
    with open(rst_path, 'r') as rst_file:
        rst_string = rst_file.read()
    return docutils_publish(rst_string, writer_name='html')['html_body']


class Build(object):

    def __init__(self, config):
        'Create config, build blog tree'
        self.config = config
        self.postpaths = self._postpaths()
        self.index = self._index()

    def _postpaths(self):
        'Get a list of rST files in configured blog root dir'
        find = ['find', self.config.blogroot, '-name', '*.rst']
        try:
            return sorted(subprocess.check_output(find,
                                                  stderr=subprocess.STDOUT)
                                    .decode('utf-8')
                                    .split(),
                          reverse=True)
        except subprocess.CalledProcessError:
            return tuple()

    def _blogtree(self):
        D = utils.OrderedDefaultdict
        blogtree = D(lambda: D(list))
        for rst_path in self.postpaths:
            meta = self.post_meta(rst_path)
            date = datetime.date(*map(int, rst_path.split(os.sep)[1:4]))
            meta['date'] = date
            blogtree[date.year][date.month].append(meta)
        return blogtree

    def _index(self):
        'Return index of all pages and posts'
        pages = [
            {'title': title, 'path': path.replace(self.config.build, '')}
            for title, path
            in map(self.page_title_buildpath, self.config.pages)
        ]
        return {'blogtree': self._blogtree(), 'pages': pages}

    def clean(self):
        'Carelessly wipe out the build dir'
        shutil.rmtree(self.config.build, ignore_errors=True)

    def render_err(self, name, context):
        'Render a template, with some debugging'
        template = self.config.get_template(name)
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

    def title_buildpath(self, root, rst_path):
        'Get the title and the build path from the path to an rST file.'
        bare_path, ext = os.path.splitext(rst_path)
        slug = os.path.split(bare_path)[-1]
        title = ' '.join(slug.split('-')).capitalize()
        buildpath = (bare_path + '.html').replace(root or self.config.blogroot,
                                                  self.config.build)
        return title, buildpath

    def prev_next(self, rst_path):
        try:
            next_index = self.postpaths.index(rst_path) - 1
            if next_index < 0:
                nextpath = nexttitle = None
            else:
                next_rst = self.postpaths[next_index]
                nexttitle, nextpath = self.title_buildpath(None, next_rst)
                nextpath = nextpath.replace(self.config.build, '')
        except IndexError:
            nextpath = nexttitle = None
        try:
            previous_rst = self.postpaths[self.postpaths.index(rst_path) + 1]
            previoustitle, previouspath = self.title_buildpath(None,
                                                               previous_rst)
            previouspath = previouspath.replace(self.config.build, '')
        except IndexError:
            previouspath = previoustitle = None
        return previouspath, previoustitle, nextpath, nexttitle

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

    def post_meta(self, rst_path):
        title, buildpath = self.title_buildpath(None, rst_path)
        previouspath, previoustitle, nextpath, nexttitle = self.prev_next(rst_path)
        commit, github_url = self.commit_github(rst_path)
        return {
            'date': datetime.date(*map(int, rst_path.split(os.sep)[1:4])),
            'title': title,
            'buildpath': buildpath,
            'nextpath': nextpath,
            'nexttitle': nexttitle,
            'previouspath': previouspath,
            'previoustitle': previoustitle,
            'github': github_url,
            'commit': commit,
        }

    def page_title_buildpath(self, rst_path):
        'Remove the pages path prefix for getting the buildpath'
        pageroot = os.path.dirname(rst_path)
        return self.title_buildpath(pageroot, rst_path)

    def page(self, rst_path):
        title, buildpath = self.page_title_buildpath(rst_path)
        context = {
            'index': self.index,
            'title': title,
            'content_html': render_rst(rst_path),
        }
        self.write_html('page.html', context, buildpath)

    def index_html(self):
        'Build the index.html'
        self.write_html(self.config.index_template,
                        {'index': self.index},
                        os.path.join(self.config.build, 'index.html'))

    def post(self, rst_path):
        context = {
            'index': self.index,
            'meta': self.post_meta(rst_path),
            'content_html': render_rst(rst_path),
        }
        buildpath = context['meta']['buildpath']
        self.write_html('post.html', context, buildpath)

    def blog_page(self):
        buildpath = (os.path.join(self.config.build, self.config.blogtree_rst)
                            .replace('rst', 'html'))
        index_rst, err = self.render_err(self.config.blogtree_rst,
                                         {'index': self.index})
        content_html = docutils_publish(index_rst, writer_name='html')['html_body']
        context = {
            'index': self.index,
            'title': 'Blog',
            'content_html': content_html,
        }
        return self.write_html('page.html', context, buildpath)

    def pages(self, pool):
        pool.map_async(self.page, self.config.pages)

    def posts(self, pool):
        pool.map_async(self.post, self.postpaths)

    def copy_assetpaths(self):
        'Copy everything specified in the config to the build directory'
        for source in self.config.assetpaths:
            destination = os.path.join(self.config.build, source)
            if os.path.isdir(source):
                shutil.copytree(source, destination)
            if os.path.isfile(source):
                shutil.copytree(source, destination)

    def sass(self):
        try:
            source = self.config.sassin,
            destination = os.path.join(self.config.build, self.config.sassout)
        except AttributeError as exc:
            if 'not configured' in str(exc):
                return
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
        print('done.')
