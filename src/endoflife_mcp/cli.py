"""The ``endoflife-mcp-server`` command line: the root app and its commands."""

from pathlib import Path
from typing import Annotated

import typer

from endoflife_mcp import __version__
from endoflife_mcp.commands.serve import serve
from endoflife_mcp.commands.version import version

app = typer.Typer(
    name="endoflife-mcp-server",
    help="An MCP server for endoflife.date: end-of-life and support dates for your AI assistant.",
    no_args_is_help=True,
    add_completion=False,
    pretty_exceptions_enable=False,
)
app.command(
    help="Run the MCP server (stdio by default). Unset options fall back to ENDOFLIFE_MCP_* "
    "environment variables, then the config file, then the defaults."
)(serve)
app.command(help="Print the installed version.")(version)


def _print_version(value: bool) -> None:
    """Print the version and exit, for the eager ``--version`` flag.

    Args:
        value: Whether ``--version`` was given.

    Raises:
        typer.Exit: Always, after printing, when ``value`` is true.
    """
    if value:
        typer.echo(__version__)
        raise typer.Exit


@app.callback()
def main(
    ctx: typer.Context,
    config: Annotated[
        Path | None,
        typer.Option(
            "--config",
            "-c",
            help="Config file (default: $XDG_CONFIG_HOME/endoflife-mcp-server/config.toml).",
            envvar="ENDOFLIFE_MCP_CONFIG",
            dir_okay=False,
        ),
    ] = None,
    show_version: Annotated[
        bool,
        typer.Option(
            "--version", help="Show the version and exit.", callback=_print_version, is_eager=True
        ),
    ] = False,
) -> None:
    """Query endoflife.date from any MCP client.

    Args:
        ctx: The Typer context; the chosen config file is stored on ``ctx.obj``.
        config: The config file to read.
        show_version: Handled by :func:`_print_version`.
    """
    ctx.obj = config
