"""Tests for the MCP server, through a real MCP client connected in-process."""

import json
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

import httpx
from mcp import Client

from endoflife_mcp.config import Settings
from endoflife_mcp.core.eol import EndOfLife
from endoflife_mcp.server import INSTRUCTIONS, build_server
from tests.conftest import load_fixture, recorded_api

TOOLS = {
    "product_list_all",
    "product_get_all",
    "product_get_cycle",
    "product_get_latest",
    "category_list",
    "category_list_products",
    "tag_list",
    "tag_list_products",
}


@asynccontextmanager
async def connect() -> AsyncIterator[Client]:
    """Connect an MCP client to a server backed by the recorded responses.

    A context manager rather than a fixture: the client's task group must be entered
    and exited in the same task, which async fixtures don't guarantee.

    Yields:
        The connected client.
    """
    service = EndOfLife(transport=httpx.MockTransport(recorded_api))
    async with Client(build_server(Settings(), service)) as connected:
        yield connected


async def call(client: Client, tool: str, **arguments: Any) -> Any:
    """Call a tool that should succeed and return its structured result.

    Args:
        client: The connected client.
        tool: Tool name.
        **arguments: Tool arguments.

    Returns:
        The tool's structured content (lists are wrapped in ``{"result": ...}``).
    """
    result = await client.call_tool(tool, arguments)
    assert not result.is_error, result.content
    assert result.structured_content is not None
    return result.structured_content


async def test_lists_every_tool_as_read_only() -> None:
    """Every tool is listed with a description and read-only annotations."""
    async with connect() as client:
        tools = (await client.list_tools()).tools
        assert {tool.name for tool in tools} == TOOLS
        for tool in tools:
            assert tool.description
            assert tool.annotations is not None
            assert tool.annotations.read_only_hint is True
            assert tool.annotations.open_world_hint is True


async def test_tool_parameters_are_described() -> None:
    """Tool parameters carry descriptions the model can read."""
    async with connect() as client:
        tools = {tool.name: tool for tool in (await client.list_tools()).tools}
        properties = tools["product_get_cycle"].input_schema["properties"]
        assert "python" in properties["product"]["description"]
        assert "3.12" in properties["cycle"]["description"]


async def test_product_tools() -> None:
    """Product tools return the API data."""
    async with connect() as client:
        names = await call(client, "product_list_all")
        assert "python" in names["result"]
        product = await call(client, "product_get_all", product="python")
        assert product["label"] == "Python"
        cycle = await call(client, "product_get_cycle", product="python", cycle="3.12")
        assert cycle == load_fixture("release_python_3.12.json")["result"]
        latest = await call(client, "product_get_latest", product="python")
        assert latest["name"] == load_fixture("release_python_latest.json")["result"]["name"]


async def test_category_and_tag_tools() -> None:
    """Category and tag tools list names and products."""
    async with connect() as client:
        assert "os" in (await call(client, "category_list"))["result"]
        assert (await call(client, "category_list_products", category="os"))["result"]
        assert "linux-distribution" in (await call(client, "tag_list"))["result"]
        products = await call(client, "tag_list_products", tag="linux-distribution")
        assert products["result"]


async def test_not_found_is_a_tool_error_with_suggestions() -> None:
    """A wrong name comes back as a tool error the model can act on."""
    async with connect() as client:
        result = await client.call_tool("product_get_all", {"product": "pyhton"})
        assert result.is_error
        text = result.content[0].text  # type: ignore[union-attr]
        assert "no product 'pyhton'" in text
        assert "Did you mean: python" in text


async def test_invalid_name_is_a_tool_error() -> None:
    """Unsafe names are refused with an explanation."""
    async with connect() as client:
        result = await client.call_tool(
            "product_get_cycle", {"product": "python", "cycle": "../.."}
        )
        assert result.is_error
        assert "not a valid release name" in result.content[0].text  # type: ignore[union-attr]


async def test_server_identity() -> None:
    """The server advertises its name and instructions."""
    server = build_server(Settings(), EndOfLife(transport=httpx.MockTransport(recorded_api)))
    async with Client(server) as connected:
        assert connected.server_info is not None
        assert connected.server_info.name == "endoflife"
        assert connected.instructions == INSTRUCTIONS


async def test_lifespan_closes_the_service() -> None:
    """The HTTP client is closed when the server shuts down."""
    service = EndOfLife(transport=httpx.MockTransport(recorded_api))
    async with Client(build_server(Settings(), service)) as connected:
        await connected.call_tool("tag_list", {})
    assert service._client.get_async_httpx_client().is_closed


async def test_results_are_json() -> None:
    """Text content mirrors the structured result as JSON."""
    async with connect() as client:
        result = await client.call_tool("product_get_cycle", {"product": "python", "cycle": "3.12"})
        assert json.loads(result.content[0].text) == result.structured_content  # type: ignore[union-attr]


async def test_default_service_uses_settings() -> None:
    """Without an injected service, one is built from the settings."""
    server = build_server(Settings(timeout=3))
    assert {tool.name for tool in await server.list_tools()} == TOOLS
