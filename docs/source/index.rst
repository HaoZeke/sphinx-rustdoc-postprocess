sphinx-rustdoc-postprocess
==========================

Post-process sphinxcontrib-rust RST output, converting leftover markdown
fragments (code fences, tables, links, headings, inline code) to proper RST
via pandoc.

Installation
------------

.. code-block:: bash

   pip install sphinx-rustdoc-postprocess

Pandoc must be available on your ``PATH``. See
`pandoc.org <https://pandoc.org/installing.html>`_ for installation
instructions.

Configuration
-------------

Add the extension to your Sphinx ``conf.py``:

.. code-block:: python

   extensions = [
       "sphinx_rustdoc_postprocess",
   ]

The following configuration values are available:

.. list-table::
   :header-rows: 1
   :widths: 40 20 40

   * - Config value
     - Default
     - Description
   * - ``rustdoc_postprocess_rst_dir``
     - ``"crates"``
     - Subdirectory of ``srcdir`` to scan for RST files.
   * - ``rustdoc_postprocess_toctree_target``
     - ``""``
     - RST file to inject a toctree snippet into. Empty = skip.
   * - ``rustdoc_postprocess_toctree_rst``
     - ``""``
     - RST snippet to append to the target file. Empty = skip.

API Reference
-------------

.. toctree::
   :maxdepth: 2

   autoapi/index
