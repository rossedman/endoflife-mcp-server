"""An MCP server that answers end-of-life and support questions from endoflife.date."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("endoflife-mcp-server")
except PackageNotFoundError:  # pragma: no cover - only when running from an uninstalled tree
    __version__ = "0.0.0"

__all__ = ["__version__"]
