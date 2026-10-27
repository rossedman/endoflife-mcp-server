"""The ``serve`` command: run the MCP server."""

import logging
from pathlib import Path
from typing import Annotated

import typer
from pydantic import ValidationError

from endoflife_mcp.config import ConfigFileNotFoundError, Transport, load_settings
from endoflife_mcp.server import build_server


def serve(
    ctx: typer.Context,
    transport: Annotated[
        Transport | None,
        typer.Option(
            help="stdio for local clients such as Claude Code; streamable-http to serve over HTTP."
        ),
    ] = None,
    host: Annotated[str | None, typer.Option(help="Address to bind for streamable-http.")] = None,
    port: Annotated[int | None, typer.Option(help="Port for streamable-http.")] = None,
    api_url: Annotated[
        str | None, typer.Option(help="Base URL of the endoflife.date v1 API.")
    ] = None,
    timeout: Annotated[
        float | None, typer.Option(help="Seconds to wait for each API request.")
    ] = None,
) -> None:
    """Run the MCP server (stdio by default).

    Options left unset fall back to ENDOFLIFE_MCP_* environment variables, then the
    config file, then the defaults.

    Args:
        ctx: The Typer context holding the config file chosen on the root command.
        transport: How MCP clients connect.
        host: Address to bind for streamable-http.
        port: Port for streamable-http.
        api_url: Base URL of the endoflife.date v1 API.
        timeout: Seconds to wait for each API request.

    Raises:
        typer.BadParameter: If a setting from any source is invalid.
        typer.Exit: With code 2 if the config file does not exist.
    """
    config: Path | None = ctx.obj
    try:
        settings = load_settings(
            config, transport=transport, host=host, port=port, api_url=api_url, timeout=timeout
        )
    except ConfigFileNotFoundError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(2) from exc
    except ValidationError as exc:
        raise typer.BadParameter(_describe(exc)) from exc
    # stdout carries the MCP protocol on stdio, so logs always go to stderr.
    logging.basicConfig(level=settings.log_level, format="%(levelname)s %(name)s: %(message)s")
    server = build_server(settings)
    if settings.transport == "stdio":
        server.run("stdio")
    else:
        server.run("streamable-http", host=settings.host, port=settings.port)


def _describe(exc: ValidationError) -> str:
    """Summarize a settings validation error as one line per invalid setting.

    Args:
        exc: The validation error raised while resolving settings.

    Returns:
        Lines such as ``port: Input should be greater than or equal to 1``.
    """
    return "\n".join(
        f"{'.'.join(str(part) for part in error['loc'])}: {error['msg']}" for error in exc.errors()
    )
