"""Sphinx configuration for sphinx-rustdoc-postprocess docs."""

project = "sphinx-rustdoc-postprocess"
author = "Rohit Goswami"
copyright = '2025, <a href="https://rgoswami.me">Rohit Goswami</a>'

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
html_theme_options = {
    "github_url": "https://github.com/HaoZeke/sphinxcontrib-rustdoc-postprocess",
    "nav_links": [
        {
            "title": "PyPI",
            "url": "https://pypi.org/project/sphinx-rustdoc-postprocess/",
            "external": True,
        },
    ],
}
