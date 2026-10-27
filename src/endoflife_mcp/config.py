"""Settings, resolved from CLI options, environment variables and a TOML config file.

Precedence, highest first: CLI option > ``ENDOFLIFE_MCP_*`` environment variable >
config file > default. The config file is ``$XDG_CONFIG_HOME/endoflife-mcp-server/config.toml``
(``~/.config/endoflife-mcp-server/config.toml`` when ``XDG_CONFIG_HOME`` is unset), or the
file passed with ``--config``.
"""

import os
from pathlib import Path
from typing import Any, Literal

from pydantic import Field, HttpUrl
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    TomlConfigSettingsSource,
)

from endoflife_mcp.core.eol import DEFAULT_API_URL

APP_NAME = "endoflife-mcp-server"
ENV_PREFIX = "ENDOFLIFE_MCP_"

Transport = Literal["stdio", "streamable-http"]


class ConfigFileNotFoundError(FileNotFoundError):
    """The config file passed with ``--config`` does not exist."""


class Settings(BaseSettings):
    """Runtime settings for the server."""

    model_config = SettingsConfigDict(env_prefix=ENV_PREFIX, extra="forbid")

    api_url: HttpUrl = Field(
        default=HttpUrl(DEFAULT_API_URL), description="Base URL of the endoflife.date v1 API."
    )
    timeout: float = Field(default=10.0, gt=0, description="Seconds to wait for each API request.")
    transport: Transport = Field(
        default="stdio", description="How MCP clients connect: stdio or streamable-http."
    )
    host: str = Field(default="127.0.0.1", description="Address to bind for streamable-http.")
    port: int = Field(default=8000, ge=1, le=65535, description="Port for streamable-http.")
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = Field(
        default="WARNING", description="Log level for messages written to stderr."
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        """Read CLI values, then the environment, then the TOML config file.

        Args:
            settings_cls: The settings class being built.
            init_settings: Values passed to the constructor (the CLI options).
            env_settings: ``ENDOFLIFE_MCP_*`` environment variables.
            dotenv_settings: Unused; ``.env`` files are not read.
            file_secret_settings: Unused; secret files are not read.

        Returns:
            The sources in precedence order.
        """
        return init_settings, env_settings, TomlConfigSettingsSource(settings_cls)


def default_config_file() -> Path:
    """Return where the config file lives when ``--config`` is not given.

    Returns:
        ``$XDG_CONFIG_HOME/endoflife-mcp-server/config.toml``, falling back to
        ``~/.config`` when ``XDG_CONFIG_HOME`` is unset or empty.
    """
    base = os.environ.get("XDG_CONFIG_HOME") or str(Path.home() / ".config")
    return Path(base) / APP_NAME / "config.toml"


def load_settings(config_file: Path | None = None, **overrides: Any) -> Settings:
    """Resolve settings from every source.

    Args:
        config_file: An explicit config file. It must exist. When ``None``, the default
            file is read if it exists.
        **overrides: Values given on the command line. ``None`` values are ignored, so
            unset options fall through to the environment and the file.

    Returns:
        The resolved settings.

    Raises:
        ConfigFileNotFoundError: If ``config_file`` is given but does not exist.
        pydantic.ValidationError: If any source holds an invalid value.
    """
    if config_file is not None and not config_file.is_file():
        raise ConfigFileNotFoundError(f"Config file not found: {config_file}")
    toml_file = config_file if config_file is not None else default_config_file()

    class FileSettings(Settings):
        """Settings bound to the config file chosen for this call."""

        model_config = SettingsConfigDict(toml_file=toml_file)

    values = {key: value for key, value in overrides.items() if value is not None}
    return Settings.model_validate(FileSettings(**values).model_dump())
