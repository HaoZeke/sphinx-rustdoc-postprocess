

# sphinx-rustdoc-postprocess

Post-process [sphinxcontrib-rust](https://github.com/aspect-build/sphinxcontrib-rust) RST output, converting leftover markdown
fragments (code fences, tables, links, headings, inline code) to proper RST
via [pandoc](https://pandoc.org/).


## The problem

[sphinxcontrib-rust](https://github.com/aspect-build/sphinxcontrib-rust) generates RST files from Rust crates, but `rustdoc`
doc-comments are written in markdown. The generated RST ends up with markdown
fragments embedded verbatim inside directive bodies, which Sphinx cannot render
correctly.

For a real-world example, see [rgpot](https://rgpot.rgoswami.me/) ([source](https://github.com/HaoZeke/rgpot)), which uses this extension to
document its Rust core library alongside C++ API docs.


### Before (raw sphinxcontrib-rust output)

Given Rust doc-comments like these in `lib.rs`:

    //! ## Module Overview
    //!
    //! | Module | Purpose |
    //! |--------|---------|
    //! | [`types`] | `#[repr(C)]` data structures for force/energy I/O |
    //! | [`tensor`] | DLPack tensor helpers |

sphinxcontrib-rust produces RST with the markdown still intact inside
directives:

    .. py:module:: rgpot_core

       ## Module Overview

       | Module | Purpose |
       |--------|---------|
       | [`types`] | `#[repr(C)]` data structures for force/energy I/O |
       | [`tensor`] | DLPack tensor helpers |

This renders incorrectly in Sphinx: headings inside directives break the
document structure, markdown tables appear as literal pipe characters, and
single-backtick code is not valid RST.


### After (postprocessed output)

After this extension runs, the same file becomes:

    .. py:module:: rgpot_core

       **Module Overview**

       +------------+----------------------------------------------------+
       | Module     | Purpose                                            |
       +============+====================================================+
       | ``types``  | ``#[repr(C)]`` data structures for force/energy IO |
       +------------+----------------------------------------------------+
       | ``tensor`` | DLPack tensor helpers                              |
       +------------+----------------------------------------------------+

Similarly, markdown code fences:

    ```c
    rgpot_status_t s = rgpot_potential_calculate(pot, &input, &output);
    if (s != RGPOT_SUCCESS) {
        fprintf(stderr, "rgpot error: %s\n", rgpot_last_error());
    }
    ```

become proper RST code-block directives:

    .. code-block:: c

       rgpot_status_t s = rgpot_potential_calculate(pot, &input, &output);
       if (s != RGPOT_SUCCESS) {
           fprintf(stderr, "rgpot error: %s\n", rgpot_last_error());
       }

And markdown links like `[metatensor](https://docs.metatensor.org/)` become
`` `metatensor <https://docs.metatensor.org/>`_ ``, while rustdoc intra-doc links
like ``[`types`]`` become `` ``types`` ``.


## Installation

    pip install sphinx-rustdoc-postprocess

Pandoc must be available on your `PATH`. See [pandoc.org](https://pandoc.org/installing.html) for installation
instructions.


## Usage

Add to your Sphinx `conf.py`:

    extensions = [
        "sphinxcontrib_rust",
        "sphinx_rustdoc_postprocess",
    ]

The extension hooks into `builder-inited` at priority 600 (after
sphinxcontrib-rust's default 500), so it automatically runs on the generated
RST files before Sphinx reads them.


### Configuration

<table border="2" cellspacing="0" cellpadding="6" rules="groups" frame="hsides">


<colgroup>
<col  class="org-left" />

<col  class="org-left" />

<col  class="org-left" />
</colgroup>
<thead>
<tr>
<th scope="col" class="org-left">Config value</th>
<th scope="col" class="org-left">Default</th>
<th scope="col" class="org-left">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td class="org-left"><code>rustdoc_postprocess_rst_dir</code></td>
<td class="org-left"><code>"crates"</code></td>
<td class="org-left">Subdirectory of <code>srcdir</code> to scan for RST files</td>
</tr>

<tr>
<td class="org-left"><code>rustdoc_postprocess_toctree_target</code></td>
<td class="org-left"><code>""</code></td>
<td class="org-left">RST file to inject a toctree snippet into (empty = skip)</td>
</tr>

<tr>
<td class="org-left"><code>rustdoc_postprocess_toctree_rst</code></td>
<td class="org-left"><code>""</code></td>
<td class="org-left">RST snippet to append to the target file (empty = skip)</td>
</tr>
</tbody>
</table>


### Full configuration example

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


## What gets converted

<table border="2" cellspacing="0" cellpadding="6" rules="groups" frame="hsides">


<colgroup>
<col  class="org-left" />

<col  class="org-left" />
</colgroup>
<thead>
<tr>
<th scope="col" class="org-left">Markdown construct</th>
<th scope="col" class="org-left">RST output</th>
</tr>
</thead>
<tbody>
<tr>
<td class="org-left"><code>```lang</code> code fences</td>
<td class="org-left"><code>.. code-block:: lang</code> directives</td>
</tr>

<tr>
<td class="org-left"><code>\vert table \vert</code> pipe tables</td>
<td class="org-left">RST grid tables (via pandoc)</td>
</tr>

<tr>
<td class="org-left"><code>[text](url)</code> links</td>
<td class="org-left"><code>`text &lt;url&gt;`_</code></td>
</tr>

<tr>
<td class="org-left"><code>[`Name`]</code> intra-doc links</td>
<td class="org-left"><code>``Name``</code></td>
</tr>

<tr>
<td class="org-left"><code>`code`</code> inline code</td>
<td class="org-left"><code>``code``</code></td>
</tr>

<tr>
<td class="org-left"><code>## Heading</code> ATX headings</td>
<td class="org-left"><code>**Heading**</code> (bold, since RST headings can't nest in directives)</td>
</tr>
</tbody>
</table>


## Development

    pixi install
    pixi run test

A `pre-commit` job is setup on CI to enforce consistent styles, so it is best
to set it up locally as well (using [uvx](https://docs.astral.sh/uv/guides/tools/) for isolation):

    # Run before committing
    uvx pre-commit run --all-files


## License

MIT
