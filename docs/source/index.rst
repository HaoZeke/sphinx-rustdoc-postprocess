

sphinx-rustdoc-postprocess
--------------------------

Post-process sphinxcontrib-rust RST output, converting leftover markdown
fragments (code fences, tables, links, headings, inline code) to proper RST
via pandoc.

.. toctree::
   :maxdepth: 2

   usage
   autoapi/index

The problem
~~~~~~~~~~~

`sphinxcontrib-rust <https://github.com/aspect-build/sphinxcontrib-rust>`_ generates RST files from Rust crates, but rustdoc
doc-comments are written in markdown. The generated RST ends up with markdown
fragments embedded verbatim inside directive bodies, which Sphinx cannot render
correctly.

For example, given Rust doc-comments with a markdown table and heading:

.. code:: rust

    //! ## Module Overview
    //!
    //! | Module | Purpose |
    //! |--------|---------|
    //! | [`types`] | `#[repr(C)]` data structures |

sphinxcontrib-rust produces RST like:

.. code:: rst

    .. py:module:: my_crate

       ## Module Overview

       | Module | Purpose |
       |--------|---------|
       | [`types`] | `#[repr(C)]` data structures |

After this extension runs, the output becomes valid RST:

.. code:: rst

    .. py:module:: my_crate

       **Module Overview**

       +----------+------------------------------+
       | Module   | Purpose                      |
       +==========+==============================+
       | ``types``| ``#[repr(C)]`` data structures|
       +----------+------------------------------+

For a real-world example, see `rgpot <https://rgpot.rgoswami.me/>`_ (`source <https://github.com/OmniPotentRPC/rgpot>`_), which uses this extension to
document its Rust core library alongside C++ API docs.
