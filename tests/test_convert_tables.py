"""Tests for _convert_tables()."""

import pytest

from sphinx_rustdoc_postprocess import _convert_tables


@pytest.mark.pandoc
def test_simple_table():
    content = """\
   | Header A | Header B |
   |----------|----------|
   | cell 1   | cell 2   |
"""
    result = _convert_tables(content)
    assert "|" not in result or "+" in result  # RST grid table uses +
    assert "Header A" in result
    assert "cell 1" in result


@pytest.mark.pandoc
def test_multi_row_table():
    content = """\
   | Col 1 | Col 2 | Col 3 |
   |-------|-------|-------|
   | a     | b     | c     |
   | d     | e     | f     |
"""
    result = _convert_tables(content)
    assert "Col 1" in result
    assert "a" in result
    assert "f" in result


@pytest.mark.pandoc
def test_table_preserves_surrounding():
    before = "   Some text before.\n\n"
    table = """\
   | H1 | H2 |
   |----|-----|
   | v1 | v2 |
"""
    after = "\n   Some text after.\n"
    content = before + table + after
    result = _convert_tables(content)
    assert "Some text before." in result
    assert "Some text after." in result


def test_no_table_unchanged():
    content = "   Just plain RST content.\n"
    assert _convert_tables(content) == content
