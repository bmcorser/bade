Introduction
############

Bade is a small command line utility to allow the user to maintain a simple
HTML website and weblog using only plaintext rST for their content. It also
bundles an rST directive (see :ref:`dotgraph`) for rendering DOT graphs as SVG.

It's very similar in spirit to some other things. It's like Pelican_ but it's a
lot simpler uses Mako_ instead of Jinja2_ and it's like Tinkerer_ but without
the dependency on Sphinx_.

I wrote it for my own usage, so typical caveats apply!

.. _Pelican: http://docs.getpelican.com/
.. _Mako: http://www.makotemplates.org/
.. _Jinja2: http://jinja.pocoo.org/docs/
.. _Tinkerer: http://tinkerer.me/
.. _Sphinx: http://sphinx-doc.org/

Plans to extend
===============
In writing Bade, I came up with a few things more I'd like to do:

    - **Git integration**: For dirty checking on build, maybe stamping a
      rendered file with its latest commit hash. There are `a few`_ GitHub
      `issues`_ for it.
    - **Markdown, etc**: It would be nice to factor out the docutils stuff to
      let the user pick their language.
    - **Hooks**: Let people hook in at interesting points, ie. call ``grunt``
      pre-build, commit after build, etc.

.. _`a few`: https://github.com/bmcorser/bade/issues/5
.. _`issues`: https://github.com/bmcorser/bade/issues/4
