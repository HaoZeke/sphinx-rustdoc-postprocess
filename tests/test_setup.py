"""Tests for the setup() entry point."""

from sphinx_rustdoc_postprocess import setup


class FakeApp:
    """Minimal stand-in for Sphinx to test setup()."""

    def __init__(self):
        self.config_values = {}
        self.connections = []

    def add_config_value(self, name, default, rebuild):
        self.config_values[name] = (default, rebuild)

    def connect(self, event, callback, priority=500):
        self.connections.append((event, callback, priority))


def test_setup_returns_metadata():
    app = FakeApp()
    result = setup(app)
    assert result["version"] == "0.1.0"
    assert result["parallel_read_safe"] is True
    assert result["parallel_write_safe"] is True


def test_setup_registers_config_values():
    app = FakeApp()
    setup(app)
    assert "rustdoc_postprocess_rst_dir" in app.config_values
    assert app.config_values["rustdoc_postprocess_rst_dir"][0] == "crates"
    assert "rustdoc_postprocess_toctree_target" in app.config_values
    assert app.config_values["rustdoc_postprocess_toctree_target"][0] == ""
    assert "rustdoc_postprocess_toctree_rst" in app.config_values
    assert app.config_values["rustdoc_postprocess_toctree_rst"][0] == ""


def test_setup_connects_builder_inited():
    app = FakeApp()
    setup(app)
    events = [e for e, _, _ in app.connections]
    assert "builder-inited" in events
    priorities = [p for e, _, p in app.connections if e == "builder-inited"]
    assert priorities[0] == 600
