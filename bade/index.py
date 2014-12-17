import datetime
import os
import subprocess

from . import utils


class BadeIndex(object):

    def __init__(self, config):
        self.config = config
        self.posts = self._posts()
        self.pages = self._pages()

    def _posts(self):
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
        for rst_path in self.posts:
            date = datetime.date(*map(int, rst_path.split(os.sep)[1:4]))
            blogtree[date.year][date.month].append({
                'date': date,
                'title': utils.rst_title(rst_path),
            })
        return blogtree

    def _pages(self):
        pages_list = list()
        for page in self.config.pages:
            if isinstance(page, str):
                pages_list.append({
                    'title': utils.rst_title(page),
                    'path': os.path.join('/', page + '.html'),
                    'build': os.path.join(self.config.build, page + '.html'),
                })
            elif isinstance(page, dict):
                title, path = page.popitem()
                pages_list.append({'title': title, 'path': path})
        return pages_list

    def _index(self):
        'Return index of all pages and posts'
        return {'blogtree': self._blogtree(), 'pages': self._pages()}

    def post_build(self, rst_path):
        'Return the path to write a rendered post'
        return (rst_path[:-4] + '.html').replace(self.config.blogroot,
                                                 self.config.build)

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

    def post_meta(self, rst_path):
        title, buildpath = self.title_buildpath(None, rst_path)
        localpath = buildpath.replace(self.config.build, '')
        previouspath, previoustitle, nextpath, nexttitle = self.prev_next(rst_path)
        commit, github_url = self.commit_github(rst_path)
        return {
            'date': datetime.date(*map(int, rst_path.split(os.sep)[1:4])),
            'title': title,
            'buildpath': buildpath,
            'localpath': localpath,
            'nextpath': nextpath,
            'nexttitle': nexttitle,
            'previouspath': previouspath,
            'previoustitle': previoustitle,
            'github': github_url,
            'commit': commit,
        }
