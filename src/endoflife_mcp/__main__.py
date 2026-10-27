"""Allow ``python -m endoflife_mcp`` to run the CLI."""

from endoflife_mcp.cli import app

app(prog_name="endoflife-mcp-server")
