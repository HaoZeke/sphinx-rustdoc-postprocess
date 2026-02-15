# sphinx-rustdoc-postprocess

Post-process [sphinxcontrib-rust](https://github.com/aspect-build/sphinxcontrib-rust) RST output, converting leftover markdown fragments (code fences, tables, links, headings, inline code) to proper RST via [pandoc](https://pandoc.org/).

## The problem

[sphinxcontrib-rust](https://github.com/aspect-build/sphinxcontrib-rust) generates RST files from Rust crates, but rustdoc doc-comments are written in markdown. The generated RST ends up with markdown fragments embedded verbatim inside directive bodies, which Sphinx cannot render correctly.

For a real-world example, see [rgpot](https://rgpot.rgoswami.me/) ([source](https://github.com/HaoZeke/rgpot)), which uses this extension to document its Rust core library alongside C++ API docs.

### Before (raw sphinxcontrib-rust output)

Given Rust doc-comments like these in `lib.rs`:

```rust
//! ## Module Overview
//!
//! | Module | Purpose |
//! |--------|---------|
//! | [`types`] | `#[repr(C)]` data structures for force/energy I/O |
//! | [`tensor`] | DLPack tensor helpers |
```

sphinxcontrib-rust produces RST with the markdown still intact inside directives:

```rst
.. py:module:: rgpot_core

   ## Module Overview

   | Module | Purpose |
   |--------|---------|
   | [`types`] | `#[repr(C)]` data structures for force/energy I/O |
   | [`tensor`] | DLPack tensor helpers |
```

This renders incorrectly in Sphinx: headings inside directives break the document structure, markdown tables appear as literal pipe characters, and single-backtick code is not valid RST.

### After (postprocessed output)

After this extension runs, the same file becomes:

```rst
.. py:module:: rgpot_core

   **Module Overview**

   +------------+----------------------------------------------------+
   | Module     | Purpose                                            |
   +============+====================================================+
   | ``types``  | ``#[repr(C)]`` data structures for force/energy IO |
   +------------+----------------------------------------------------+
   | ``tensor`` | DLPack tensor helpers                              |
   +------------+----------------------------------------------------+
```

Similarly, markdown code fences:

```rst
   ```c
   rgpot_status_t s = rgpot_potential_calculate(pot, &input, &output);
   if (s != RGPOT_SUCCESS) {
       fprintf(stderr, "rgpot error: %s\n", rgpot_last_error());
   }
   ```
```

become proper RST code-block directives:

```rst
   .. code-block:: c

      rgpot_status_t s = rgpot_potential_calculate(pot, &input, &output);
      if (s != RGPOT_SUCCESS) {
          fprintf(stderr, "rgpot error: %s\n", rgpot_last_error());
      }
```

And markdown links like `[metatensor](https://docs.metatensor.org/)` become `` `metatensor <https://docs.metatensor.org/>`_ ``, while rustdoc intra-doc links like `` [`types`] `` become ``` ``types`` ```.

## Installation

```bash
pip install sphinx-rustdoc-postprocess
```

Pandoc must be available on your `PATH`. See [pandoc.org](https://pandoc.org/installing.html) for installation instructions.

## Usage

Add to your Sphinx `conf.py`:

```python
extensions = [
    "sphinxcontrib_rust",
    "sphinx_rustdoc_postprocess",
]
```

The extension hooks into `builder-inited` at priority 600 (after sphinxcontrib-rust's default 500), so it automatically runs on the generated RST files before Sphinx reads them.

### Configuration

| Config value | Default | Description |
|---|---|---|
| `rustdoc_postprocess_rst_dir` | `"crates"` | Subdirectory of `srcdir` to scan for RST files |
| `rustdoc_postprocess_toctree_target` | `""` | RST file to inject a toctree snippet into (empty = skip) |
| `rustdoc_postprocess_toctree_rst` | `""` | RST snippet to append to the target file (empty = skip) |

### Example: full configuration

```python
# conf.py
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
```

## What gets converted

| Markdown construct | RST output |
|---|---|
| ` ```lang ` code fences | `.. code-block:: lang` directives |
| `\| table \|` pipe tables | RST grid tables (via pandoc) |
| `[text](url)` links | `` `text <url>`_ `` |
| `` [`Name`] `` intra-doc links | ``` ``Name`` ``` |
| `` `code` `` inline code | ``` ``code`` ``` |
| `## Heading` ATX headings | `**Heading**` (bold, since RST headings can't nest in directives) |

## Development

```bash
pixi install
pixi run test
```

## License

MIT
