# sphinx-rustdoc-postprocess

Post-process [sphinxcontrib-rust](https://github.com/aspect-build/sphinxcontrib-rust) RST output, converting leftover markdown fragments (code fences, tables, links, headings, inline code) to proper RST via [pandoc](https://pandoc.org/).

## Installation

```bash
pip install sphinx-rustdoc-postprocess
```

Pandoc must be available on your `PATH`. See [pandoc.org](https://pandoc.org/installing.html) for installation instructions.

## Usage

Add to your Sphinx `conf.py`:

```python
extensions = [
    "sphinx_rustdoc_postprocess",
]
```

### Configuration

| Config value | Default | Description |
|---|---|---|
| `rustdoc_postprocess_rst_dir` | `"crates"` | Subdirectory of `srcdir` to scan for RST files |
| `rustdoc_postprocess_toctree_target` | `""` | RST file to inject a toctree snippet into (empty = skip) |
| `rustdoc_postprocess_toctree_rst` | `""` | RST snippet to append to the target file (empty = skip) |

## Development

```bash
pixi install
pixi run test
```

## License

MIT
