"""Sphinx configuration for sphinx-rustdoc-postprocess docs."""

project = "sphinx-rustdoc-postprocess"
author = "Rohit Goswami"
copyright = "2025, Rohit Goswami"

extensions = [
    "autoapi.extension",
    "sphinx.ext.intersphinx",
]

autoapi_dirs = ["../../src"]
autoapi_type = "python"

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "sphinx": ("https://www.sphinx-doc.org/en/master", None),
}

html_theme = "shibuya"
