

Usage
-----

Installation
~~~~~~~~~~~~

.. code:: bash

    pip install sphinx-rustdoc-postprocess

Pandoc must be available on your ``PATH``. See `pandoc.org <https://pandoc.org/installing.html>`_ for installation
instructions.

Configuration
~~~~~~~~~~~~~

Add the extension to your Sphinx ``conf.py``:

.. code:: python

    extensions = [
        "sphinxcontrib_rust",
        "sphinx_rustdoc_postprocess",
    ]

The extension hooks into ``builder-inited`` at priority 600 (after
sphinxcontrib-rust's default 500), so it automatically runs on the generated
RST files before Sphinx reads them.

The following configuration values are available:

.. table::

    +----------------------------------------+--------------+----------------------------------------------------------+
    | Config value                           | Default      | Description                                              |
    +========================================+==============+==========================================================+
    | ``rustdoc_postprocess_rst_dir``        | ``"crates"`` | Subdirectory of ``srcdir`` to scan for RST files         |
    +----------------------------------------+--------------+----------------------------------------------------------+
    | ``rustdoc_postprocess_toctree_target`` | ``""``       | RST file to inject a toctree snippet into (empty = skip) |
    +----------------------------------------+--------------+----------------------------------------------------------+
    | ``rustdoc_postprocess_toctree_rst``    | ``""``       | RST snippet to append to the target file (empty = skip)  |
    +----------------------------------------+--------------+----------------------------------------------------------+

Full example
~~~~~~~~~~~~

.. code:: python

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

What gets converted
~~~~~~~~~~~~~~~~~~~

.. table::

    +------------------------------+-----------------------------------------------------------------------+
    | Markdown construct           | RST output                                                            |
    +==============================+=======================================================================+
    | `````lang`` code fences      | ``.. code-block:: lang`` directives                                   |
    +------------------------------+-----------------------------------------------------------------------+
    | pipe tables                  | RST grid tables (via pandoc)                                          |
    +------------------------------+-----------------------------------------------------------------------+
    | ``[text](url)`` links        | ```text <url>`_``                                                     |
    +------------------------------+-----------------------------------------------------------------------+
    | ``[`Name`]`` intra-doc links | ````Name````                                                          |
    +------------------------------+-----------------------------------------------------------------------+
    | ```code``` inline code       | ````code````                                                          |
    +------------------------------+-----------------------------------------------------------------------+
    | ``## Heading`` ATX headings  | ``\*\*Heading**`` (bold, since RST headings can't nest in directives) |
    +------------------------------+-----------------------------------------------------------------------+
