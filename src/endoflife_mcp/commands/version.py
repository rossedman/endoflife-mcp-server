"""The ``version`` command."""

import typer

from endoflife_mcp import __version__


def version() -> None:
    """Print the installed version."""
    typer.echo(__version__)
