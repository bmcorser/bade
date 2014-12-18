.. _documentation:

Documentation
#############

Colophon
========


Bade mostly leans on other things.

    - **Docutils / rST**: Bade uses Docutils to process plaintext rST documents
      into markup, which will be familiar to Python developers. Probably the
      most useful resource is their `quick reference`_, but there is full
      documentation available on the `Docutils homepage`_.
    - **Mako**: Templates are rendered with Mako_, a templating engine written
      by zzzeek_. It has inheritance, is fast and lets your do whatever.

.. _`quick reference`: http://docutils.sourceforge.net/
.. _`Docutils homepage`: http://docutils.sourceforge.net/docs/user/rst/quickref.html
.. _Mako: http://www.makotemplates.org/
.. _zzzeek: http://techspot.zzzeek.org/

.. _templates:

Templates
=========
Bade uses a bunch of templates which are pretty empty and intended to be simple
to customise to the specific applications. The best way to get an idea of how
things are laid out is to `look at the markup`_ and see how the ``<%block>``
elements are arranged in the ``base.html`` template on GitHub.

.. _`look at the markup`: https://github.com/bmcorser/bade/blob/master/templates/base.html


.. _context:

Context
-------

Another interesting template to look at would be the ``header.html`` template
that lists links to pages. The ``pages`` and ``blogtree`` context variable

.. _blogtree:

Blogtree
========

The way that Bade tells where posts appear chronologically is rather manual.
It's the responsibility of the user to place the content of their pose in a
tree of directories where the first level denotes year, the second month and
the third day. It's covered in the :ref:`posts` section of the :ref:`tutorial`.

.. _configuration:

Configuration
=============

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
Path to custom rST template for blog index page. Example:

.. code-block:: yaml

    blogtree_rst: templates/blogtree.rst

``build``
---------
Directory to build in. Example:

.. code-block:: yaml

    build: _build

``debug``
---------

Just asks Mako for :ref:`debugging` output. Override with ``--debug`` on the
command line. Example:

.. code-block:: yaml

    debug: true

``index_template``
------------------
The template to look up to render the front page of the site. Example:

.. code-block:: yaml

    index_template: index.html

``pages``
---------
Pages and external links, string is a page, dict is an external link. Example:

.. code-block:: yaml

    pages:
      - pages/about
      - pages/projects
      - github: https://github.com/johndoe

``template_dirs``
-----------------
Directories to add to Mako TemplateLookup_ used by Bade (ie. the most preferred
templates come first). The packaged templates are always part of this lookup,
so if a required template isn't found in a directory listed here, it will be
available. Example:

.. code-block:: yaml

    template_dirs:
      - templates
      - summer_templates
      - winter_templates

.. _TemplateLookup: http://docs.makotemplates.org/en/latest/usage.html#using-templatelookup
