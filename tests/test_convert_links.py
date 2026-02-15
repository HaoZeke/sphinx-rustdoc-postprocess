"""Tests for _convert_links() and _convert_inline_code()."""

from sphinx_rustdoc_postprocess import _convert_inline_code, _convert_links


class TestConvertLinks:
    def test_md_link_to_rst(self):
        content = "   See [docs](https://example.com) for more."
        result = _convert_links(content)
        assert "`docs <https://example.com>`_" in result
        assert "[docs]" not in result

    def test_intradoc_link(self):
        content = "   See [`MyStruct`] for details."
        result = _convert_links(content)
        assert "``MyStruct``" in result
        assert "[`MyStruct`]" not in result

    def test_double_backtick_intradoc(self):
        content = "   See [``SomeType``] for details."
        result = _convert_links(content)
        assert "``SomeType``" in result

    def test_rst_directive_skipped(self):
        content = "   .. some-directive:: arg"
        assert _convert_links(content) == content

    def test_rst_field_skipped(self):
        content = "   :param name: some [text](https://url.com)"
        assert _convert_links(content) == content

    def test_no_links_unchanged(self):
        content = "   Plain text without links."
        assert _convert_links(content) == content


class TestConvertInlineCode:
    def test_single_to_double_backtick(self):
        content = "   Use `foo` for this."
        result = _convert_inline_code(content)
        assert "``foo``" in result
        assert result.count("``") == 2  # one pair

    def test_already_double_backtick_unchanged(self):
        content = "   Use ``foo`` for this."
        result = _convert_inline_code(content)
        assert result == content

    def test_rst_directive_skipped(self):
        content = "   .. code-block:: `python`"
        assert _convert_inline_code(content) == content

    def test_rst_field_skipped(self):
        content = "   :param `name`: value"
        assert _convert_inline_code(content) == content

    def test_rst_link_not_mangled(self):
        content = "   `text <https://url.com>`_"
        result = _convert_inline_code(content)
        assert result == content
