Tutorial
########

You should get a grip of things running through this tutorial (there's not much
to get), but if you want to know more, please refer to the
:ref:`Documentation`.

Assumptions
===========

This tutorial and indeed Bade itself are written with a few assumptions.

    - You intend to serve from ``/``
    - You're in a \*nix shell
    - You're using Python 3.x
    - You're in a Git_ repo

Of course you are!

.. _Git: http://www.git-scm.com/

Setup
=====
Bade is configured by YAML file (vaguely inspired by Grunt_) which holds
something like a site map and paths to template and asset directories. The
default name for Bade's configuration YAML is ``bade.yaml`` [#]_, so let's
create that file and add some basic configuration:

.. _Grunt: http://gruntjs.com/

.. code-block:: yaml

    blogtitle: Blog
    pages:
      - pages/about-me
      - github: https://github.com

We've specified two pages, one is a local "about" page and the other is an
external link to github. The first is a string ``pages/about-me`` and tells
Bade there is an rST document ``pages/about-me.rst`` that should be rendered
and added to the site navigation list, the second is a mapping of name to URL
which should also be added to the navigation list, but since it's an external
link no rST needs to be rendered. The order pages are specified in the YAML is
significant; it's the order they will be rendered in the navigation list. In
the next section we'll create our "About me" page.

.. [#] You can call it something else and specify that on the command line


Pages
=====

Pages are rST documents that want to be rendered and added to the site, but not
included in the blog. Links to them are provided in the :ref:`context` to all
:ref:`templates`.

Let's make a ``pages`` directory and put a page there.

.. code-block:: bash

    mkdir pages
    touch pages/about-me.rst

And throw some rST in that file.

.. code-block:: rst

    About me
    ########

    I like biscuits, especially custard creams.

This is the page that is referred to in our configuration YAML:

.. code-block:: yaml

    pages:
      - pages/about-me

Add all this stuff to Git and commit it:

.. code-block:: shell

    git add pages bade.yaml
    git commit -m 'Added about page'

The title of the page is derived from the file name, in this case the file
``about-me.rst`` will be titled ``About me``. This holds for posts too.

We could render our site now, but let's add a post first ...

.. _posts:

Posts
=====

Posts are almost the same deal as Pages_, except they must appear in a
directory structure like looking like this (it's used as a faux index) and
don't need to be explicitly added to ``bade.yaml``::

    blog
    └── 2014
        ├── 07
        │   ├── 10
        │   │   ├── evening.rst
        │   │   └── morning.rst
        │   └── 16
        │       └── next-week.rst
        ├── 09
        │   └── 14
        │       └── entry.rst
        └── 12
            └── 16
                └── today.rst

The default directory for posts is ``blog``, but this can be configured [#]_. The
directory for "today" can be created with some shell subsitution:

.. code-block:: shell

    mkdir -p blog/$(date +'%Y/%m/%d')

You can add an rST file to the "today" directory the same way (unless it turned
midnight as you were typing):

.. code-block:: shell

    touch blog/$(date +'%Y/%m/%d')/exciting-news.rst

Throw some rST in that file and tell Git about it:

.. code-block:: shell

    git add blog
    git commit -m 'Added blog post'

Let's render our micro-blog for the first time.

.. code-block:: shell

    bade

The HTML for the rST files we created above will be rendered in a directory
called ``_build`` (of course, this can be changed in :ref:`configuration`). You
can serve from that directory for development. Things are looking pretty plain
right now, so after a brief overview of configuration options, we'll look at
how to add styles and use our own templates.

Before we forget, let's also tell Git to ignore that pesky ``_build``
directory:

.. code-block:: shell

    echo '_build' >> .gitignore

.. [#] See :ref:`configuration` for all the options.

Build
=====

When you build your site, rST is rendered to HTML and jammed into page or post
templates, the :ref:`Blogtree` and site index are rendered. Any assets
specified for inclusion are also copied to the build directory. Optionally
SCSS/Sass is compiled.

Templating
----------
The templates provided with Bade are simple, a little bit semantic and work out
of the box. However, they are plain as you like and don't have any styles_! To
start hacking your own templates together, download the "template" templates
from GitHub_ and go crazy. Let's follow a quick example for changing up our
site index to welcome visitors.

.. _GitHub: https://github.com/bmcorser/bade/tree/master/templates

First grab the remote ``index.html`` template and put it in ``templates`` [#]_
locally:

.. code-block:: shell

    mkdir templates
    curl https://raw.githubusercontent.com/bmcorser/bade/master/templates/index.html > templates/index.html

It looks like this:

.. code-block:: mako

    <%inherit file="base.html"/>

    <%block name="title_block">Index</%block>

    <%block name="header_block"></%block>

    <%block name="content_block">
        <ul>
        % for page in index['pages']:
            <li>
                <a href="${page['path']}">${page['title']}</a>
            </li>
        % endfor
            <li><a href="/blog.html">Blog</a></li>
        </ul>
    </%block>

Let's knock out the ``header`` block [#]_ to use the default inherited from
``base.html``. Let's also add a big welcome message. Your ``index.html`` will
now look like this:

.. code-block:: mako

    <%inherit file="base.html"/>

    <%block name="title_block">Yes, this is blog.</%block>

    <%block name="content_block">
        <h1>Hello, computer!</h1>
    </%block>

Let's build again by running ``bade`` and check things are looking how we
expect. This is cool, but our blog is still looking plain. Let's spice it up a
bit by adding some CSS and images.

.. [#] This is the default templates directory, but can be configured (see
       :ref:`configuration`).
.. [#] In the example above, an empty *but specified* block will override the
       parent template's block -- even if it has some content.

Assets
------
By default, everything in a directory called ``assets`` will be copied to the
build directory and be available at ``/assets`` when serving.

Anything else your site needs apart from its rendered rST can be included by
adding to the ``assetpaths`` list in the configuration YAML. Let's see how to
add styles and put an image in blog post

Styles
^^^^^^
First create an assets directory and add a stylesheet that will make our site
look really cool:

.. code-block:: shell

    mkdir -p assets/css
    touch assets/css/styles.css

Red text? I rather think so. Everyone likes red text.

.. code-block:: css

    body {
      color: red;
    }
Next we need to include this in our templates, so we need to override another
default, this time the ``base.html`` where our ``<head>`` is specified. Let's
grab is like we did before:

.. code-block:: shell

    curl https://raw.githubusercontent.com/bmcorser/bade/master/templates/base.html > templates/base.html

The base template is pretty simple, it pretty much just provides a few blocks
to override:

.. code-block:: mako

    <html>
        <head>
            <meta charset="UTF-8">
            <title><%block name="title_block">${title}</%block></title>
        </head>
        <body>
            <%block name="header_block">
                <%include file="header.html" />
            </%block>
            <%block name="content_block" />
            <%block name="footer_block" />
        </body>
    </html>

Add the ``<link>`` somewhere in the ``<head>`` the path should treat the build
directory as root:

.. code-block:: html

    <link href="/assets/css/styles.css" rel="stylesheet" type="text/css" />

Build the site by invoking ``bade`` and check the technique! It's all red, yo.

Images
^^^^^^

Including images in the build is as easy as dumping them in the assets
directory. Local images can then be referenced from your rST in an ``image``
directive. Let's try it, first let's get an image in our assets directory:

.. code-block:: shell

    mkdir assets/images
    curl https://www.python.org/static/img/python-logo@2x.png > assets/images/python.png

Then alter ``pages/about-me.rst`` to reference this image:

.. code-block:: rst

    About me
    ########

    I like biscuits, especially custard creams.

    I write ...

    .. image:: /assets/images/python.png

Debugging templates
===================
Bade hooks into Mako's excellent debugging output with the ``--debug`` flag.
Once the build is completed, there'll be a message pointing you to files to
inspect through the browser::

    Debug HTML written to: ../_build/about.html

