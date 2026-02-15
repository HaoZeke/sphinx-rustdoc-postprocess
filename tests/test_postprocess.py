"""Integration tests for postprocess_rst_files() and inject_rust_toctree()."""

from sphinx_rustdoc_postprocess import inject_rust_toctree, postprocess_rst_files


def test_postprocess_converts_fences(mock_app, write_rst):
    rst = write_rst(
        "mymod.rst",
        """\
.. py:function:: foo()

   ```rust
   let x = 1;
   ```
""",
    )
    postprocess_rst_files(mock_app)
    result = rst.read_text(encoding="utf-8")
    assert ".. code-block:: rust" in result
    assert "```" not in result


def test_postprocess_converts_links(mock_app, write_rst):
    rst = write_rst(
        "mymod.rst",
        """\
.. py:function:: foo()

   See [docs](https://example.com) for more.
""",
    )
    postprocess_rst_files(mock_app)
    result = rst.read_text(encoding="utf-8")
    assert "`docs <https://example.com>`_" in result


def test_postprocess_converts_headings(mock_app, write_rst):
    rst = write_rst(
        "mymod.rst",
        """\
.. py:function:: foo()

   ## Examples
""",
    )
    postprocess_rst_files(mock_app)
    result = rst.read_text(encoding="utf-8")
    assert "**Examples**" in result


def test_postprocess_converts_inline_code(mock_app, write_rst):
    rst = write_rst(
        "mymod.rst",
        """\
.. py:function:: foo()

   Use `bar` here.
""",
    )
    postprocess_rst_files(mock_app)
    result = rst.read_text(encoding="utf-8")
    assert "``bar``" in result


def test_postprocess_unchanged_file_not_rewritten(mock_app, write_rst):
    content = """\
.. py:function:: foo()

   Already proper RST.
"""
    rst = write_rst("clean.rst", content)
    mtime_before = rst.stat().st_mtime_ns
    postprocess_rst_files(mock_app)
    mtime_after = rst.stat().st_mtime_ns
    assert mtime_before == mtime_after


def test_postprocess_nonexistent_dir(mock_app, tmp_path):
    """No error when the rst dir doesn't exist."""
    mock_app.config.rustdoc_postprocess_rst_dir = "nonexistent"
    postprocess_rst_files(mock_app)


def test_inject_toctree(mock_app, tmp_srcdir):
    target = tmp_srcdir / "api" / "index.rst"
    target.parent.mkdir(parents=True)
    target.write_text("API Index\n=========\n", encoding="utf-8")

    toctree_snippet = """
Rust API
--------

.. toctree::
   :maxdepth: 2

   ../crates/mylib/lib
"""
    mock_app.config.rustdoc_postprocess_toctree_target = "api/index.rst"
    mock_app.config.rustdoc_postprocess_toctree_rst = toctree_snippet

    inject_rust_toctree(mock_app)
    result = target.read_text(encoding="utf-8")
    assert "Rust API" in result
    assert "../crates/mylib/lib" in result


def test_inject_toctree_skips_when_empty_config(mock_app):
    """No injection when config values are empty."""
    inject_rust_toctree(mock_app)


def test_inject_toctree_idempotent(mock_app, tmp_srcdir):
    target = tmp_srcdir / "index.rst"
    target.write_text("Index\n=====\n", encoding="utf-8")

    snippet = "\n.. toctree::\n\n   crates/lib\n"
    mock_app.config.rustdoc_postprocess_toctree_target = "index.rst"
    mock_app.config.rustdoc_postprocess_toctree_rst = snippet

    inject_rust_toctree(mock_app)
    inject_rust_toctree(mock_app)
    result = target.read_text(encoding="utf-8")
    assert result.count("crates/lib") == 1
