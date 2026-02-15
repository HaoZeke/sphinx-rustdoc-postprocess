sphinx-rustdoc-postprocess
==========================

Post-process sphinxcontrib-rust RST output, converting leftover markdown
fragments (code fences, tables, links, headings, inline code) to proper RST
via pandoc.

The problem
-----------

`sphinxcontrib-rust <https://github.com/aspect-build/sphinxcontrib-rust>`_
generates RST files from Rust crates, but rustdoc doc-comments are written in
markdown. The generated RST ends up with markdown fragments embedded verbatim
inside directive bodies, which Sphinx cannot render correctly.

For example, given Rust doc-comments with a markdown table and heading:

.. code-block:: rust

   //! ## Module Overview
   //!
   //! | Module | Purpose |
   //! |--------|---------|
   //! | [`types`] | `#[repr(C)]` data structures |

sphinxcontrib-rust produces RST like:

.. code-block:: rst

   .. py:module:: my_crate

      ## Module Overview

      | Module | Purpose |
      |--------|---------|
      | [`types`] | `#[repr(C)]` data structures |

After this extension runs, the output becomes valid RST:

.. code-block:: rst

   .. py:module:: my_crate

      **Module Overview**

      +----------+------------------------------+
      | Module   | Purpose                      |
      +==========+==============================+
      | ``types``| ``#[repr(C)]`` data structures|
      +----------+------------------------------+

For a real-world example, see `rgpot <https://rgpot.rgoswami.me/>`_
(`source <https://github.com/HaoZeke/rgpot>`_), which uses this extension to
document its Rust core library alongside C++ API docs.

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
       "sphinxcontrib_rust",
       "sphinx_rustdoc_postprocess",
   ]

The extension hooks into ``builder-inited`` at priority 600 (after
sphinxcontrib-rust's default 500), so it automatically runs on the generated
RST files before Sphinx reads them.

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

What gets converted
-------------------

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - Markdown construct
     - RST output
   * - `````lang`` code fences
     - ``.. code-block:: lang`` directives
   * - ``| table |`` pipe tables
     - RST grid tables (via pandoc)
   * - ``[text](url)`` links
     - ```text <url>`_``
   * - ``[`Name`]`` intra-doc links
     - ````Name````
   * - ```code``` inline code
     - ````code````
   * - ``## Heading`` ATX headings
     - ``**Heading**`` (bold, since RST headings can't nest in directives)

Full example
------------

.. code-block:: python

   # conf.py
   import os

   extensions = [
       "sphinxcontrib_rust",
       "sphinx_rustdoc_postprocess",
   ]

   # sphinxcontrib-rust settings
   rust_crates = {
       "my_crate": os.path.abspath("../../my-crate/"),
   }
   rust_doc_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "crates")
   rust_rustdoc_fmt = "rst"

   # Inject a toctree entry for the Rust docs into an existing index page
   rustdoc_postprocess_toctree_target = "api/index.rst"
   rustdoc_postprocess_toctree_rst = """

   Rust API
   --------

   .. toctree::
      :maxdepth: 2

      ../crates/my_crate/lib
   """

API Reference
-------------

.. toctree::
   :maxdepth: 2

   autoapi/index
