.. _documentation:

Documentation
#############

Docutils / rST
==============

Mako
====

.. _templates:

Templates
=========

.. _context:

Context
-------

``base.html``
-------------

``index.html``
--------------

``header.html``
---------------

``page.html``
-------------

``post.html``
-------------

``blog.html``
-------------

``prev_next.html``
------------------



.. _blogtree:

Blogtree
========

The way that Bade tells where :ref:`Posts` appear chronologically is rather
manual. A tree of directories with branches

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


