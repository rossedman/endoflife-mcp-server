"""Tests for the command line, run without a TTY through Typer's CliRunner."""

import runpy
import sys
from pathlib import Path
from typing import Any

import pytest
from mcp.server.mcpserver import MCPServer
from typer.testing import CliRunner

from endoflife_mcp import __version__
from endoflife_mcp.cli import app

runner = CliRunner()


@pytest.fixture(autouse=True)
def isolated_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep the user's config file and ENDOFLIFE_MCP_* variables out of the tests.

    Args:
        tmp_path: Per-test temp directory.
        monkeypatch: Pytest's monkeypatch fixture.
    """
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "xdg"))
    for name in ("API_URL", "TIMEOUT", "TRANSPORT", "HOST", "PORT", "LOG_LEVEL", "CONFIG"):
        monkeypatch.delenv(f"ENDOFLIFE_MCP_{name}", raising=False)


@pytest.fixture
def runs(monkeypatch: pytest.MonkeyPatch) -> list[tuple[str, dict[str, Any]]]:
    """Record MCPServer.run calls instead of starting a server.

    Args:
        monkeypatch: Pytest's monkeypatch fixture.

    Returns:
        The recorded ``(transport, kwargs)`` calls.
    """
    calls: list[tuple[str, dict[str, Any]]] = []

    def fake_run(self: MCPServer, transport: str = "stdio", **kwargs: Any) -> None:
        calls.append((transport, kwargs))

    monkeypatch.setattr(MCPServer, "run", fake_run)
    return calls


def test_no_args_shows_help() -> None:
    """Running with no command prints help listing the commands."""
    result = runner.invoke(app, [])
    assert "serve" in result.output
    assert "version" in result.output


@pytest.mark.parametrize("args", [["--version"], ["version"]])
def test_version(args: list[str]) -> None:
    """Both the flag and the command print the version."""
    result = runner.invoke(app, args)
    assert result.exit_code == 0
    assert result.output.strip() == __version__


def test_serve_defaults_to_stdio(runs: list[tuple[str, dict[str, Any]]]) -> None:
    """The serve command runs the stdio transport by default."""
    result = runner.invoke(app, ["serve"])
    assert result.exit_code == 0, result.output
    assert runs == [("stdio", {})]


def test_serve_streamable_http(runs: list[tuple[str, dict[str, Any]]]) -> None:
    """streamable-http binds the configured host and port."""
    args = ["serve", "--transport", "streamable-http", "--host", "0.0.0.0", "--port", "9000"]  # noqa: S104
    result = runner.invoke(app, args)
    assert result.exit_code == 0, result.output
    assert runs == [("streamable-http", {"host": "0.0.0.0", "port": 9000})]  # noqa: S104


def test_serve_reads_env_and_config(
    runs: list[tuple[str, dict[str, Any]]], tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """--config and environment variables feed serve, with options on top."""
    config = tmp_path / "config.toml"
    config.write_text('transport = "streamable-http"\nport = 9100\n', encoding="utf-8")
    monkeypatch.setenv("ENDOFLIFE_MCP_HOST", "::1")
    result = runner.invoke(app, ["--config", str(config), "serve", "--port", "9200"])
    assert result.exit_code == 0, result.output
    assert runs == [("streamable-http", {"host": "::1", "port": 9200})]


def test_serve_missing_config_file(runs: list[tuple[str, dict[str, Any]]], tmp_path: Path) -> None:
    """A missing --config file exits 2 with a clear message."""
    result = runner.invoke(app, ["-c", str(tmp_path / "missing.toml"), "serve"])
    assert result.exit_code == 2
    assert "Config file not found" in result.output
    assert runs == []


def test_serve_invalid_setting(
    runs: list[tuple[str, dict[str, Any]]], monkeypatch: pytest.MonkeyPatch
) -> None:
    """An invalid setting from any source is a usage error naming the setting."""
    monkeypatch.setenv("ENDOFLIFE_MCP_TIMEOUT", "-1")
    result = runner.invoke(app, ["serve"])
    assert result.exit_code == 2
    assert "timeout" in result.output
    assert runs == []


def test_python_dash_m(monkeypatch: pytest.MonkeyPatch) -> None:
    """Running the package with ``python -m`` gives the same CLI."""
    monkeypatch.setattr(sys, "argv", ["endoflife-mcp-server", "version"])
    with pytest.raises(SystemExit) as info:
        runpy.run_module("endoflife_mcp", run_name="__main__")
    assert info.value.code == 0
