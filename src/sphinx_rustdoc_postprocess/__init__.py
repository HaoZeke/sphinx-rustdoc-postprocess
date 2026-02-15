"""Post-process sphinxcontrib-rust RST output via pandoc.

sphinxcontrib-rust dumps rustdoc (markdown) doc-comments verbatim into RST
directive bodies.  This extension runs *after* sphinxcontrib_rust's
``builder-inited`` handler (priority 600 > default 500), walks the generated
``.rst`` files, extracts the markdown content blocks, and converts them to
proper RST through ``pandoc -f markdown -t rst``.
"""

from __future__ import annotations

import re
import subprocess
import textwrap
from pathlib import Path

from sphinx.application import Sphinx
from sphinx.util import logging

_log = logging.getLogger(__name__)

# Matches an indented markdown fenced code block:
#   <indent>```lang
#   ...code...
#   <indent>```
_FENCE_RE = re.compile(
    r"^(?P<indent>[ ]+)```(?P<lang>\w*)\s*\n"
    r"(?P<body>.*?)"
    r"^(?P=indent)```[ ]*$",
    re.MULTILINE | re.DOTALL,
)

# Matches an indented markdown table (header + separator + rows).
_TABLE_RE = re.compile(
    r"^(?P<indent>[ ]+)\|.+\|[ ]*\n"  # header row
    r"(?P=indent)\|[-| :]+\|[ ]*\n"  # separator row
    r"(?:(?P=indent)\|.+\|[ ]*\n)+",  # data rows
    re.MULTILINE,
)

# Matches an indented markdown ATX heading (## Heading).
_HEADING_RE = re.compile(
    r"^(?P<indent>[ ]+)(?P<hashes>#{1,6})[ ]+(?P<text>.+)$",
    re.MULTILINE,
)

# Matches markdown inline code (`code`) that is NOT already double-backtick RST.
# Handles the common case where `code`<letter> breaks RST inline markup rules.
# Excludes <> so RST links (`text <url>`_) are not mangled.
_INLINE_CODE_RE = re.compile(
    r"(?<!`)(`)((?!`)(?:[^`\n<>])+)\1(?!`)",
)

# Matches markdown hyperlinks: [text](url)
_MD_LINK_RE = re.compile(
    r"\[(?P<text>[^\[\]]+)\]\((?P<url>https?://[^)]+)\)",
)

# Matches rustdoc intra-doc links: [`code`] or [``code``] (without a URL part).
_INTRADOC_LINK_RE = re.compile(
    r"\[`{1,2}(?P<name>[^`\]]+)`{1,2}\](?!\()",
)


def _pandoc(markdown: str) -> str:
    """Convert a markdown fragment to RST via pandoc.

    Parameters
    ----------
    markdown : str
        The markdown text to convert.

    Returns
    -------
    str
        The converted RST text, or the original markdown if pandoc fails.
    """
    result = subprocess.run(
        ["pandoc", "-f", "markdown-smart", "-t", "rst", "--wrap=none"],
        input=markdown,
        capture_output=True,
        text=True,
        timeout=10,
    )
    if result.returncode != 0:
        _log.warning("[rustdoc_postprocess] pandoc failed: %s", result.stderr)
        return markdown
    return result.stdout


def _convert_fences(content: str) -> str:
    """Convert markdown code fences to RST code-block directives.

    Parameters
    ----------
    content : str
        RST file content potentially containing indented markdown code fences.

    Returns
    -------
    str
        Content with code fences replaced by ``.. code-block::`` directives.
    """

    def _replace(m: re.Match) -> str:
        indent = m.group("indent")
        lang = m.group("lang") or "none"
        body = m.group("body")

        body_indent = indent + "   "
        lines = []
        for line in body.split("\n"):
            stripped = line.rstrip()
            if stripped:
                if stripped.startswith(indent):
                    stripped = stripped[len(indent) :]
                lines.append(body_indent + stripped)
            else:
                lines.append("")
        while lines and not lines[-1].strip():
            lines.pop()

        body_text = "\n".join(lines)
        return f"{indent}.. code-block:: {lang}\n\n{body_text}\n"

    return _FENCE_RE.sub(_replace, content)


def _convert_tables(content: str) -> str:
    """Convert markdown tables to RST tables via pandoc.

    Parameters
    ----------
    content : str
        RST file content potentially containing indented markdown tables.

    Returns
    -------
    str
        Content with markdown tables replaced by RST grid tables.
    """

    def _replace(m: re.Match) -> str:
        indent = m.group("indent")
        table_md = textwrap.dedent(m.group(0))
        rst = _pandoc(table_md).rstrip("\n")
        lines = [indent + line if line.strip() else "" for line in rst.split("\n")]
        return "\n".join(lines) + "\n"

    return _TABLE_RE.sub(_replace, content)


def _convert_links(content: str) -> str:
    """Convert markdown links to RST.

    Parameters
    ----------
    content : str
        RST file content potentially containing markdown-style links.

    Returns
    -------
    str
        Content with ``[text](url)`` converted to ```text <url>`_`` and
        rustdoc intra-doc links ``[`name`]`` converted to ````name````.
    """

    def _process_line(line: str) -> str:
        stripped = line.lstrip()
        if stripped.startswith("..") or stripped.startswith(":"):
            return line
        line = _MD_LINK_RE.sub(r"`\g<text> <\g<url>>`_", line)
        line = _INTRADOC_LINK_RE.sub(r"``\g<name>``", line)
        return line

    return "\n".join(_process_line(line) for line in content.split("\n"))


def _convert_inline_code(content: str) -> str:
    """Convert markdown inline code to RST double-backtick literals.

    Parameters
    ----------
    content : str
        RST file content potentially containing markdown single-backtick code.

    Returns
    -------
    str
        Content with single-backtick code converted to double-backtick literals.
    """

    def _process_line(line: str) -> str:
        stripped = line.lstrip()
        if stripped.startswith("..") or stripped.startswith(":"):
            return line
        return _INLINE_CODE_RE.sub(r"``\2``", line)

    return "\n".join(_process_line(line) for line in content.split("\n"))


def _convert_headings(content: str) -> str:
    """Convert markdown ATX headings to bold labels.

    RST section headings cannot appear inside directive bodies, so we
    convert ``## Heading`` to ``**Heading**`` which renders as bold.

    Parameters
    ----------
    content : str
        RST file content potentially containing markdown ATX headings.

    Returns
    -------
    str
        Content with headings replaced by bold text.
    """

    def _replace(m: re.Match) -> str:
        indent = m.group("indent")
        text = m.group("text").strip()
        return f"{indent}**{text}**"

    return _HEADING_RE.sub(_replace, content)


def postprocess_rst_files(app: Sphinx) -> None:
    """Walk generated RST files and convert markdown fragments.

    Scans the directory specified by the ``rustdoc_postprocess_rst_dir``
    config value (relative to ``app.srcdir``) for ``.rst`` files and applies
    all markdown-to-RST conversions in sequence.

    Parameters
    ----------
    app : Sphinx
        The Sphinx application instance.
    """
    rst_dir = Path(app.srcdir) / app.config.rustdoc_postprocess_rst_dir
    if not rst_dir.exists():
        return

    for rst_file in sorted(rst_dir.rglob("*.rst")):
        original = rst_file.read_text(encoding="utf-8")
        converted = original
        converted = _convert_fences(converted)
        converted = _convert_links(converted)
        converted = _convert_tables(converted)
        converted = _convert_headings(converted)
        converted = _convert_inline_code(converted)
        if converted != original:
            _log.info(
                "[rustdoc_postprocess] Converted markdown in %s",
                rst_file.relative_to(app.srcdir),
            )
            rst_file.write_text(converted, encoding="utf-8")


def inject_rust_toctree(app: Sphinx) -> None:
    """Append a toctree snippet to a target RST file.

    Reads the ``rustdoc_postprocess_toctree_target`` and
    ``rustdoc_postprocess_toctree_rst`` config values. If either is empty,
    the injection is skipped.

    Parameters
    ----------
    app : Sphinx
        The Sphinx application instance.
    """
    target = app.config.rustdoc_postprocess_toctree_target
    toctree_rst = app.config.rustdoc_postprocess_toctree_rst
    if not target or not toctree_rst:
        return

    target_path = Path(app.srcdir) / target
    if not target_path.exists():
        return

    content = target_path.read_text(encoding="utf-8")
    if toctree_rst.strip() in content:
        return

    target_path.write_text(content.rstrip("\n") + "\n" + toctree_rst, encoding="utf-8")
    _log.info("[rustdoc_postprocess] Injected toctree into %s", target)


def _on_builder_inited(app: Sphinx) -> None:
    """builder-inited callback: postprocess then inject toctree."""
    postprocess_rst_files(app)
    inject_rust_toctree(app)


def setup(app: Sphinx) -> dict:
    """Register the extension with Sphinx.

    Parameters
    ----------
    app : Sphinx
        The Sphinx application instance.

    Returns
    -------
    dict
        Extension metadata with version and parallel safety flags.
    """
    app.add_config_value("rustdoc_postprocess_rst_dir", "crates", "env")
    app.add_config_value("rustdoc_postprocess_toctree_target", "", "env")
    app.add_config_value("rustdoc_postprocess_toctree_rst", "", "env")
    app.connect("builder-inited", _on_builder_inited, priority=600)
    return {
        "version": "0.1.0",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
