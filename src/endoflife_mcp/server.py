"""The MCP server: endoflife.date queries exposed as read-only MCP tools."""

from collections.abc import AsyncIterator, Awaitable
from contextlib import asynccontextmanager
from typing import Annotated, Any, TypeVar

from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from mcp.types import ToolAnnotations
from pydantic import Field

from endoflife_mcp import __version__
from endoflife_mcp.config import Settings
from endoflife_mcp.core.eol import EndOfLife
from endoflife_mcp.core.errors import EndOfLifeError

INSTRUCTIONS = """\
Answers questions about software end-of-life and support dates using endoflife.date.

Start with product_get_all for a product (it includes every release cycle), or
product_get_cycle for a single cycle such as python 3.12. Product names are slugs such as
python, kubernetes or amazon-eks; common aliases (k8s, postgres) also work. When a name is
not found, the error suggests close matches. Use product_list_all, or the category and tag
tools, to discover names. Dates are ISO 8601; a null date with a true flag means the date
is not known yet."""

READ_ONLY = ToolAnnotations(read_only_hint=True, open_world_hint=True, idempotent_hint=True)

ProductName = Annotated[
    str, Field(description="Product name or alias, such as python, kubernetes or amazon-eks.")
]
ReleaseName = Annotated[
    str, Field(description="Release cycle name as listed in the product's releases, e.g. 3.12.")
]

T = TypeVar("T")


async def _run(call: Awaitable[T]) -> T:
    """Await a service call, turning anticipated failures into tool errors.

    The model then sees the service's message (for example, suggested product names)
    instead of a generic failure.

    Args:
        call: The pending service call.

    Returns:
        The call's result.

    Raises:
        ToolError: If the service raised an :class:`EndOfLifeError`.
    """
    try:
        return await call
    except EndOfLifeError as exc:
        raise ToolError(str(exc)) from exc


def build_server(settings: Settings, service: EndOfLife | None = None) -> MCPServer:
    """Create the MCP server and register its tools.

    Args:
        settings: Resolved settings.
        service: The endoflife.date service to use. By default one is built from
            ``settings`` and closed when the server shuts down.

    Returns:
        The server, ready to run.
    """
    eol = service or EndOfLife(str(settings.api_url), settings.timeout)

    @asynccontextmanager
    async def lifespan(_: MCPServer) -> AsyncIterator[None]:
        """Close the HTTP client when the server stops.

        Yields:
            Nothing; the server runs while the context is open.
        """
        try:
            yield
        finally:
            await eol.aclose()

    server: MCPServer = MCPServer(
        "endoflife",
        title="endoflife.date",
        instructions=INSTRUCTIONS,
        website_url="https://github.com/rossedman/endoflife-mcp-server",
        version=__version__,
        log_level=settings.log_level,
        lifespan=lifespan,
    )

    @server.tool(annotations=READ_ONLY)
    async def product_list_all() -> list[str]:
        """List the name of every product endoflife.date tracks (about 500).

        Returns:
            Product names, such as python, kubernetes and amazon-eks.
        """
        return await _run(eol.product_names())

    @server.tool(annotations=READ_ONLY)
    async def product_get_all(product: ProductName) -> dict[str, Any]:
        """Get a product with all of its release cycles and their support and end-of-life dates.

        Args:
            product: Product name or alias.

        Returns:
            The product: label, category, tags, links and every release cycle.
        """
        return await _run(eol.product(product))

    @server.tool(annotations=READ_ONLY)
    async def product_get_cycle(product: ProductName, cycle: ReleaseName) -> dict[str, Any]:
        """Get one release cycle of a product, such as python 3.12.

        Args:
            product: Product name or alias.
            cycle: Release cycle name.

        Returns:
            The release cycle: release, support and end-of-life dates, LTS status and
            latest version.
        """
        return await _run(eol.release(product, cycle))

    @server.tool(annotations=READ_ONLY)
    async def product_get_latest(product: ProductName) -> dict[str, Any]:
        """Get the newest release cycle of a product.

        Args:
            product: Product name or alias.

        Returns:
            The latest release cycle, in the same shape as product_get_cycle.
        """
        return await _run(eol.latest_release(product))

    @server.tool(annotations=READ_ONLY)
    async def category_list() -> list[str]:
        """List the product categories, such as lang, os, database and framework.

        Returns:
            Category names.
        """
        return await _run(eol.categories())

    @server.tool(annotations=READ_ONLY)
    async def category_list_products(
        category: Annotated[str, Field(description="A category name from category_list.")],
    ) -> list[dict[str, Any]]:
        """List the products in a category, such as every database endoflife.date tracks.

        Args:
            category: Category name.

        Returns:
            A summary (name, label, aliases, category, tags) of each product.
        """
        return await _run(eol.category_products(category))

    @server.tool(annotations=READ_ONLY)
    async def tag_list() -> list[str]:
        """List the product tags, such as linux-distribution, amazon or cncf.

        Returns:
            Tag names.
        """
        return await _run(eol.tags())

    @server.tool(annotations=READ_ONLY)
    async def tag_list_products(
        tag: Annotated[str, Field(description="A tag name from tag_list.")],
    ) -> list[dict[str, Any]]:
        """List the products with a tag, such as every managed Kubernetes service.

        Args:
            tag: Tag name.

        Returns:
            A summary (name, label, aliases, category, tags) of each product.
        """
        return await _run(eol.tag_products(tag))

    return server
