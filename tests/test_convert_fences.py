"""Tests for _convert_fences()."""

from sphinx_rustdoc_postprocess import _convert_fences


def test_rust_fence():
    content = """\
   ```rust
   let x = 1;
   ```
"""
    result = _convert_fences(content)
    assert ".. code-block:: rust" in result
    assert "let x = 1;" in result
    assert "```" not in result


def test_fence_no_lang_defaults_to_none():
    content = """\
   ```
   some code
   ```
"""
    result = _convert_fences(content)
    assert ".. code-block:: none" in result


def test_fence_preserves_indent():
    content = """\
      ```python
      print("hello")
      ```
"""
    result = _convert_fences(content)
    assert "      .. code-block:: python" in result


def test_multiple_fences():
    content = """\
   ```rust
   let a = 1;
   ```
   ```python
   x = 2
   ```
"""
    result = _convert_fences(content)
    assert ".. code-block:: rust" in result
    assert ".. code-block:: python" in result
    assert "```" not in result


def test_no_fence_unchanged():
    content = "   Just plain RST content.\n"
    assert _convert_fences(content) == content
