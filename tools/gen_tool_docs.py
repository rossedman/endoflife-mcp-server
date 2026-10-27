"""Write docs/reference/tools.md from the tools the MCP server actually registers.

Run with ``uv run python tools/gen_tool_docs.py`` (``make docs`` does). The page is built from
``server.list_tools()``, so it cannot drift from the code.
"""

import asyncio
import inspect
from pathlib import Path
from typing import Any

from endoflife_mcp.config import Settings
from endoflife_mcp.server import build_server

OUTPUT = Path("docs/reference/tools.md")

INTRO = """\
# Tools

Every tool the server registers, generated from the running server by
`tools/gen_tool_docs.py`. All of them are read-only: they only query endoflife.date and
never change anything. For worked examples with real output, see the
[tools guide](../tools.md).

"""


def split_description(description: str) -> tuple[str, str]:
    """Split a Google-style tool docstring into its summary and its ``Returns`` text.

    Args:
        description: The tool description as the server publishes it.

    Returns:
        The text before ``Args:``/``Returns:``, and the text of the ``Returns:`` section
        (empty when there is none), each with whitespace normalised.
    """
    text = inspect.cleandoc(description)
    summary, _, rest = text.partition("\n\nArgs:")
    summary, _, returns = summary.partition("\n\nReturns:")
    if rest:
        _, _, returns = rest.partition("Returns:")
    return summary.strip(), " ".join(returns.split())


def parameter_table(schema: dict[str, Any]) -> str:
    """Render a tool's input schema as a Markdown table.

    Args:
        schema: The JSON schema of the tool's arguments.

    Returns:
        A table with one row per parameter, or a line saying there are none.
    """
    properties: dict[str, Any] = schema.get("properties", {})
    if not properties:
        return "This tool takes no parameters.\n"
    required = set(schema.get("required", []))
    rows = ["| Parameter | Type | Required | Description |", "| --- | --- | --- | --- |"]
    for name, prop in properties.items():
        needed = "yes" if name in required else "no"
        rows.append(
            f"| `{name}` | {prop.get('type', 'any')} | {needed} | {prop.get('description', '')} |"
        )
    return "\n".join(rows) + "\n"


def render_tool(name: str, description: str, schema: dict[str, Any]) -> str:
    """Render one tool as a Markdown section.

    Args:
        name: The tool name.
        description: The tool description as the server publishes it.
        schema: The JSON schema of the tool's arguments.

    Returns:
        The section: heading, summary, parameters and what it returns.
    """
    summary, returns = split_description(description)
    parts = [f"## `{name}`\n", f"{summary}\n", parameter_table(schema)]
    if returns:
        parts.append(f"**Returns:** {returns}\n")
    return "\n".join(parts)


async def build_page() -> str:
    """Build the whole tools reference page.

    Returns:
        The Markdown text of ``docs/reference/tools.md``.
    """
    server = build_server(Settings())
    tools = await server.list_tools()
    sections = [render_tool(t.name, t.description or "", t.input_schema) for t in tools]
    return INTRO + "\n".join(sections)


def main() -> None:
    """Generate the page and write it to :data:`OUTPUT`."""
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(asyncio.run(build_page()), encoding="utf-8")
    print(f"wrote {OUTPUT}")


if __name__ == "__main__":
    main()
