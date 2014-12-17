Tutorial
########

You should get a grip of things running through this tutorial (there's not much
to get), but if you want to know more, please refer to the
:ref:`Documentation`.

Assumptions
===========

This tutorial and indeed Bade itself are written with a few assumptions.

    - You're in a \*nix shell
    - You're using Python 3.x
    - You're in a venv_
    - You're in a Git_ repo

Of course you are!

.. _Git: http://www.git-scm.com/
.. _venv: https://docs.python.org/3/library/venv.html

Pages
=====

Pages are rST documents that will be rendered but not included in the
":ref:`Blogtree`".

Let's make a ``pages`` directory and put a page there.

.. code-block:: bash

    mkir pages
    touch pages/about.rst

And throw some rST in that file.

.. code-block:: rst

    About me
    ########

    I like cakes.

We need to let Bade know that we've added a page, so let's add an entry to
``bade.yaml``, which should look something like this:

.. code-block:: yaml

    pages:
      - pages/about

Add all this stuff to Git and commit it:

.. code-block:: shell

    git add pages bade.yaml
    commit -m 'Added about page'

We could render our site now, but let's add a post first ...

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

The directory for "today" can be created with some shell subsitution:

.. code-block:: shell

    mkdir -p blog/$(date +'%Y/%m/%d')

You can add an rST file to the "today" directory the same way (unless it turned
midnight as you were reading):

.. code-block:: shell

    touch blog/$(date +'%Y/%m/%d')/exciting-news.rst

Throw some rST in that file and let's render our micro-blog for the first time.

.. code-block:: shell

    bade

The HTML for the rST files we created above will be rendered in a directory
called ``_build`` (of course, this can be changed in Config_). You can
serve from that directory for development. Things are looking pretty plain
right now, so after a brief overview of configuration options, we'll look at
how to add styles and use our own templates.

Before we forget, let's also tell Git to ignore that pesky ``_build``
directory:

.. code-block:: shell

    echo '_build' >> .gitignore


Config
======

Bade has a few options which can be configured through keys in a YAML file.
Their effects are detailed below.

``assetpaths``
--------------
A list of directory paths containing any assets to be copied to the build
directory. Directory will be preserved. Example:

.. code-block:: yaml

    assetpaths:
      - assets/images
      - assets/js
      - assets/fonts

``blogroot``
------------
The directory where the tree of Posts_ will appear. Example:

.. code-block:: yaml

    blogroot: blog

``blogtree_rst``
----------------
Path to custom rST template for :ref:`Blogtree`. Example:

.. code-block:: yaml

    blogtree_rst: templates/blogtree.rst

``build``
---------
Directory to build in. Example:

.. code-block:: yaml

    build: _build

``debug``
---------
Example:

.. code-block:: yaml

    blogroot: blog

``index_template``
------------------
Example:

.. code-block:: yaml

    blogroot: blog

``pages``
---------
Example:

.. code-block:: yaml

    blogroot: blog

``template_dirs``
-----------------
Directories to add to Mako TemplateLookup_ used by Bade. Example:

.. code-block:: yaml

    template_dirs:
      - templates
      - christmas_templates

.. _TemplateLookup: http://docs.makotemplates.org/en/latest/usage.html#using-templatelookup


Build
=====

Assets
------

Styles
^^^^^^

Images
^^^^^^

Publishing
==========

Debugging
=========

