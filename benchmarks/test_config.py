"""Benchmark settings resolution across the CLI, environment and config file."""

from pathlib import Path

import pytest
from pytest_benchmark.fixture import BenchmarkFixture

from endoflife_mcp.config import load_settings


def test_load_settings_from_every_source(
    benchmark: BenchmarkFixture, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Resolve settings with a config file, an env var and a CLI override all set."""
    config = tmp_path / "config.toml"
    config.write_text('timeout = 5\nhost = "localhost"\n', encoding="utf-8")
    monkeypatch.setenv("ENDOFLIFE_MCP_PORT", "9000")
    settings = benchmark(load_settings, config, transport="streamable-http")
    assert (settings.timeout, settings.port, settings.transport) == (5, 9000, "streamable-http")
