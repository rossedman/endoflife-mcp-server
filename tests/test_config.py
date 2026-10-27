"""Tests for settings resolution: CLI > environment > config file > default."""

from pathlib import Path

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st
from pydantic import ValidationError

from endoflife_mcp.config import (
    ConfigFileNotFoundError,
    Settings,
    default_config_file,
    load_settings,
)


@pytest.fixture(autouse=True)
def isolated_config(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Point the default config file at an empty temp dir and clear ENDOFLIFE_MCP_* vars.

    Args:
        tmp_path: Per-test temp directory.
        monkeypatch: Pytest's monkeypatch fixture.

    Returns:
        The XDG config home used for the test.
    """
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "xdg"))
    for name in ("API_URL", "TIMEOUT", "TRANSPORT", "HOST", "PORT", "LOG_LEVEL"):
        monkeypatch.delenv(f"ENDOFLIFE_MCP_{name}", raising=False)
    return tmp_path / "xdg"


def write_default_config(xdg: Path, text: str) -> Path:
    """Write the default config file.

    Args:
        xdg: The XDG config home.
        text: TOML content.

    Returns:
        The config file path.
    """
    path = xdg / "endoflife-mcp-server" / "config.toml"
    path.parent.mkdir(parents=True)
    path.write_text(text, encoding="utf-8")
    return path


def test_defaults() -> None:
    """With no sources, the defaults apply."""
    settings = load_settings()
    assert settings == Settings()
    assert str(settings.api_url) == "https://endoflife.date/api/v1"
    assert settings.transport == "stdio"
    assert settings.timeout == 10.0


def test_default_config_file_uses_xdg(isolated_config: Path) -> None:
    """The default file lives under XDG_CONFIG_HOME."""
    assert default_config_file() == isolated_config / "endoflife-mcp-server" / "config.toml"


def test_default_config_file_falls_back_to_home(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Without XDG_CONFIG_HOME, the file lives under ~/.config."""
    monkeypatch.delenv("XDG_CONFIG_HOME")
    monkeypatch.setenv("HOME", str(tmp_path))
    assert default_config_file() == tmp_path / ".config" / "endoflife-mcp-server" / "config.toml"


def test_precedence_cli_over_env_over_file(
    isolated_config: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Each source overrides the ones below it, setting by setting."""
    write_default_config(isolated_config, 'timeout = 1\nport = 9001\nhost = "0.0.0.0"\n')
    monkeypatch.setenv("ENDOFLIFE_MCP_TIMEOUT", "2")
    monkeypatch.setenv("ENDOFLIFE_MCP_PORT", "9002")
    settings = load_settings(port=9003)
    assert settings.host == "0.0.0.0"  # noqa: S104 - from the file, not a bind
    assert settings.timeout == 2.0  # env beats file
    assert settings.port == 9003  # CLI beats env


def test_none_overrides_fall_through(monkeypatch: pytest.MonkeyPatch) -> None:
    """Unset CLI options (None) don't mask the environment."""
    monkeypatch.setenv("ENDOFLIFE_MCP_TRANSPORT", "streamable-http")
    assert load_settings(transport=None).transport == "streamable-http"


def test_explicit_config_file(tmp_path: Path) -> None:
    """--config reads the given file instead of the default."""
    path = tmp_path / "custom.toml"
    path.write_text('api_url = "https://eol.example.com/api/v1"\n', encoding="utf-8")
    assert str(load_settings(path).api_url) == "https://eol.example.com/api/v1"


def test_missing_explicit_config_file(tmp_path: Path) -> None:
    """A --config file that doesn't exist is an error, not silently ignored."""
    with pytest.raises(ConfigFileNotFoundError, match=r"custom\.toml"):
        load_settings(tmp_path / "custom.toml")


@pytest.mark.parametrize(
    "text",
    [
        "timeout = 0\n",
        "port = 70000\n",
        'transport = "sse"\n',
        'api_url = "not a url"\n',
        "nope = 1\n",
    ],
)
def test_invalid_file_values(isolated_config: Path, text: str) -> None:
    """Invalid or unknown settings in the file are rejected."""
    write_default_config(isolated_config, text)
    with pytest.raises(ValidationError):
        load_settings()


@pytest.mark.fuzz
@settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(
    timeout=st.text(max_size=20),
    port=st.text(max_size=20),
    transport=st.text(max_size=20),
)
def test_env_values_validate_or_raise(
    monkeypatch: pytest.MonkeyPatch, timeout: str, port: str, transport: str
) -> None:
    """Any environment values give valid settings or a ValidationError, never anything else."""
    for name, value in (("TIMEOUT", timeout), ("PORT", port), ("TRANSPORT", transport)):
        if "\x00" in value:
            return  # the OS can't hold a NUL in an environment variable
        monkeypatch.setenv(f"ENDOFLIFE_MCP_{name}", value)
    try:
        settings = load_settings()
    except ValidationError:
        return
    assert settings.timeout > 0
    assert 1 <= settings.port <= 65535
    assert settings.transport in {"stdio", "streamable-http"}
