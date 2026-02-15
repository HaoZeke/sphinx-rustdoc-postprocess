"""Tests for _convert_headings()."""

from sphinx_rustdoc_postprocess import _convert_headings


def test_h2_heading():
    content = "   ## My Section"
    result = _convert_headings(content)
    assert result.strip() == "**My Section**"


def test_h3_heading():
    content = "   ### Sub Section"
    result = _convert_headings(content)
    assert result.strip() == "**Sub Section**"


def test_h1_heading():
    content = "   # Top Level"
    result = _convert_headings(content)
    assert result.strip() == "**Top Level**"


def test_preserves_indent():
    content = "      ## Indented"
    result = _convert_headings(content)
    assert result == "      **Indented**"


def test_multiple_headings():
    content = "   ## First\n   ### Second\n"
    result = _convert_headings(content)
    assert "**First**" in result
    assert "**Second**" in result
    assert "##" not in result


def test_no_heading_unchanged():
    content = "   Just plain RST content.\n"
    assert _convert_headings(content) == content


def test_heading_at_start_of_line_not_matched():
    """Headings must be indented (inside directive bodies)."""
    content = "## Top Level"
    assert _convert_headings(content) == content
