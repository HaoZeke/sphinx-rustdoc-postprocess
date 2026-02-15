"""Shared fixtures and markers for sphinx_rustdoc_postprocess tests."""

from __future__ import annotations

import shutil
from pathlib import Path
from types import SimpleNamespace

import pytest


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "pandoc: marks tests that require pandoc on PATH"
    )


def pytest_collection_modifyitems(config, items):
    if shutil.which("pandoc") is None:
        skip_pandoc = pytest.mark.skip(reason="pandoc not found on PATH")
        for item in items:
            if "pandoc" in item.keywords:
                item.add_marker(skip_pandoc)


@pytest.fixture()
def tmp_srcdir(tmp_path):
    """Create a temporary Sphinx srcdir with a crates/ subdirectory."""
    crates = tmp_path / "crates"
    crates.mkdir()
    return tmp_path


@pytest.fixture()
def mock_app(tmp_srcdir):
    """Return a minimal mock Sphinx app with config attributes."""
    config = SimpleNamespace(
        rustdoc_postprocess_rst_dir="crates",
        rustdoc_postprocess_toctree_target="",
        rustdoc_postprocess_toctree_rst="",
    )
    app = SimpleNamespace(srcdir=str(tmp_srcdir), config=config)
    return app


@pytest.fixture()
def write_rst(tmp_srcdir):
    """Helper fixture that writes an RST file under crates/ and returns its path."""

    def _write(name: str, content: str) -> Path:
        p = tmp_srcdir / "crates" / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return p

    return _write
