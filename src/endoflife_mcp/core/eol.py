"""The endoflife.date service: typed, validated calls to the endoflife.date v1 API.

Requests go through the client generated from ``api/external/endoflife.yaml``; this
module adds name validation, error mapping and the shapes the MCP tools return.
"""

from collections.abc import Awaitable, Callable
from http import HTTPStatus
from types import TracebackType
from typing import Any, Self, TypeVar

import httpx

from endoflife_mcp import __version__
from endoflife_mcp.client import Client
from endoflife_mcp.client.api.categories import categories as categories_endpoint
from endoflife_mcp.client.api.categories import products_category
from endoflife_mcp.client.api.products import (
    product,
    product_release,
    product_release_latest,
    products,
)
from endoflife_mcp.client.api.tags import products_tag
from endoflife_mcp.client.api.tags import tags as tags_endpoint
from endoflife_mcp.client.models.product_list_response import ProductListResponse
from endoflife_mcp.client.models.product_release_response import ProductReleaseResponse
from endoflife_mcp.client.models.product_response import ProductResponse
from endoflife_mcp.client.models.product_summary import ProductSummary
from endoflife_mcp.client.models.uri_list_response import UriListResponse
from endoflife_mcp.client.types import Response
from endoflife_mcp.core.errors import NotFoundError, RateLimitedError, UpstreamError
from endoflife_mcp.core.names import normalize_release, normalize_slug
from endoflife_mcp.core.suggest import suggest_products

DEFAULT_API_URL = "https://endoflife.date/api/v1"
"""The public endoflife.date v1 API."""

USER_AGENT = (
    f"endoflife-mcp-server/{__version__} (+https://github.com/rossedman/endoflife-mcp-server)"
)
"""Sent with every request so endoflife.date can tell where traffic comes from."""

T = TypeVar("T")


class EndOfLife:
    """An async client for the endoflife.date API that returns plain JSON-ready data.

    Use it as an async context manager, or call :meth:`aclose` when done, so the
    underlying HTTP connection pool is released.
    """

    def __init__(
        self,
        api_url: str = DEFAULT_API_URL,
        timeout: float = 10.0,
        *,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        """Create the service.

        Args:
            api_url: Base URL of the endoflife.date v1 API.
            timeout: Seconds to wait for each request before giving up.
            transport: An httpx transport to send requests through instead of the
                network, used by tests.
        """
        httpx_args: dict[str, Any] = {} if transport is None else {"transport": transport}
        self._client = Client(
            base_url=api_url.rstrip("/"),
            timeout=httpx.Timeout(timeout),
            follow_redirects=True,
            headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
            httpx_args=httpx_args,
        )

    async def __aenter__(self) -> Self:
        """Enter the context, returning the service itself.

        Returns:
            This service.
        """
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        """Close the HTTP client when the context exits.

        Args:
            exc_type: The exception type, if the block raised.
            exc: The exception, if the block raised.
            tb: The traceback, if the block raised.
        """
        await self.aclose()

    async def aclose(self) -> None:
        """Close the underlying HTTP client."""
        await self._client.get_async_httpx_client().aclose()

    async def product_summaries(self) -> list[ProductSummary]:
        """Fetch the summary of every product endoflife.date tracks.

        Returns:
            One summary per product, in the API's order.

        Raises:
            EndOfLifeError: If the request fails.
        """
        response = await self._call(products.asyncio_detailed, ProductListResponse, "products list")
        return response.result

    async def product_names(self) -> list[str]:
        """List the canonical name of every product endoflife.date tracks.

        Returns:
            Product names such as ``python`` or ``amazon-eks``, in the API's order.

        Raises:
            EndOfLifeError: If the request fails.
        """
        return [summary.name for summary in await self.product_summaries()]

    async def product(self, name: str) -> dict[str, Any]:
        """Fetch everything endoflife.date knows about a product, including all releases.

        Aliases (``k8s``) are resolved to the canonical product (``kubernetes``).

        Args:
            name: The product name or alias.

        Returns:
            The product details, as JSON-ready data.

        Raises:
            InvalidNameError: If ``name`` cannot be a product name.
            NotFoundError: If there is no such product; the message suggests close names.
            EndOfLifeError: If the request fails for another reason.
        """
        slug = normalize_slug(name)
        response = await self._call(
            product.asyncio_detailed, ProductResponse, f"product {slug!r}", slug, product=slug
        )
        return response.result.to_dict()

    async def release(self, product_name: str, release: str) -> dict[str, Any]:
        """Fetch one release cycle of a product, such as Python ``3.12``.

        Args:
            product_name: The product name or alias.
            release: The release cycle name, as listed in the product's releases.

        Returns:
            The release cycle, as JSON-ready data.

        Raises:
            InvalidNameError: If either name is invalid.
            NotFoundError: If the product or the release cycle does not exist.
            EndOfLifeError: If the request fails for another reason.
        """
        slug = normalize_slug(product_name)
        cycle = normalize_release(release)
        response = await self._call(
            product_release.asyncio_detailed,
            ProductReleaseResponse,
            f"release {cycle!r} of product {slug!r}",
            slug,
            cycle,
            product=slug,
        )
        return response.result.to_dict()

    async def latest_release(self, product_name: str) -> dict[str, Any]:
        """Fetch the newest release cycle of a product.

        Args:
            product_name: The product name or alias.

        Returns:
            The latest release cycle, as JSON-ready data.

        Raises:
            InvalidNameError: If the name is invalid.
            NotFoundError: If the product does not exist.
            EndOfLifeError: If the request fails for another reason.
        """
        slug = normalize_slug(product_name)
        response = await self._call(
            product_release_latest.asyncio_detailed,
            ProductReleaseResponse,
            f"product {slug!r}",
            slug,
            product=slug,
        )
        return response.result.to_dict()

    async def categories(self) -> list[str]:
        """List the product categories, such as ``lang``, ``os`` or ``database``.

        Returns:
            Category names.

        Raises:
            EndOfLifeError: If the request fails.
        """
        response = await self._call(
            categories_endpoint.asyncio_detailed, UriListResponse, "categories list"
        )
        return [uri.name for uri in response.result]

    async def category_products(self, category: str) -> list[dict[str, Any]]:
        """List the products in a category.

        Args:
            category: A category name from :meth:`categories`.

        Returns:
            A summary of each product in the category.

        Raises:
            InvalidNameError: If the name is invalid.
            NotFoundError: If the category does not exist.
            EndOfLifeError: If the request fails for another reason.
        """
        slug = normalize_slug(category, "category")
        response = await self._call(
            products_category.asyncio_detailed, ProductListResponse, f"category {slug!r}", slug
        )
        return [_summary(item) for item in response.result]

    async def tags(self) -> list[str]:
        """List the product tags, such as ``linux-distribution`` or ``amazon``.

        Returns:
            Tag names.

        Raises:
            EndOfLifeError: If the request fails.
        """
        response = await self._call(tags_endpoint.asyncio_detailed, UriListResponse, "tags list")
        return [uri.name for uri in response.result]

    async def tag_products(self, tag: str) -> list[dict[str, Any]]:
        """List the products with a tag.

        Args:
            tag: A tag name from :meth:`tags`.

        Returns:
            A summary of each product with the tag.

        Raises:
            InvalidNameError: If the name is invalid.
            NotFoundError: If the tag does not exist.
            EndOfLifeError: If the request fails for another reason.
        """
        slug = normalize_slug(tag, "tag")
        response = await self._call(
            products_tag.asyncio_detailed, ProductListResponse, f"tag {slug!r}", slug
        )
        return [_summary(item) for item in response.result]

    async def _call(
        self,
        endpoint: Callable[..., Awaitable[Response[Any]]],
        expected: type[T],
        what: str,
        *args: str,
        product: str | None = None,
    ) -> T:
        """Call a generated endpoint and map every failure to an :class:`EndOfLifeError`.

        Args:
            endpoint: A generated ``asyncio_detailed`` function.
            expected: The model type a successful response parses into.
            what: What was requested, for error messages (``"product 'python'"``).
            *args: Path parameters, in the endpoint's order.
            product: The product name, when the request is about one product; a 404 then
                looks up similar product names to suggest.

        Returns:
            The parsed response.

        Raises:
            NotFoundError: On HTTP 404.
            RateLimitedError: On HTTP 429.
            UpstreamError: When the API is unreachable, answers with another status, or
                returns a body that doesn't match the spec.
        """
        try:
            response = await endpoint(*args, client=self._client)
        except httpx.HTTPError as exc:
            raise UpstreamError(f"Could not reach endoflife.date: {exc}") from exc
        except (KeyError, TypeError, ValueError) as exc:
            raise UpstreamError(
                f"endoflife.date returned a {what} response that does not match its API spec."
            ) from exc
        if response.status_code == HTTPStatus.OK and isinstance(response.parsed, expected):
            return response.parsed
        if response.status_code == HTTPStatus.NOT_FOUND:
            raise NotFoundError(await self._not_found_message(what, product))
        if response.status_code == HTTPStatus.TOO_MANY_REQUESTS:
            raise RateLimitedError(response.headers.get("Retry-After"))
        raise UpstreamError(
            f"endoflife.date answered the {what} request with HTTP {int(response.status_code)}."
        )

    async def _not_found_message(self, what: str, product: str | None) -> str:
        """Build the message for a 404, suggesting product names when one was requested.

        Suggestions are best effort: if the products list can't be fetched, the
        message simply has none.

        Args:
            what: What was requested.
            product: The requested product name, if any.

        Returns:
            The error message.
        """
        message = f"endoflife.date has no {what}."
        if product is None:
            return message
        try:
            summaries = await self.product_summaries()
        except (UpstreamError, RateLimitedError):
            return message
        if any(summary.name == product for summary in summaries):
            return message
        suggestions = suggest_products(product, summaries)
        if suggestions:
            message += " Did you mean: " + ", ".join(suggestions) + "?"
        return message


def _summary(item: ProductSummary) -> dict[str, Any]:
    """Convert a product summary to JSON-ready data without its API URL.

    Args:
        item: A product summary from a list endpoint.

    Returns:
        The summary's name, label, aliases, category and tags.
    """
    data = item.to_dict()
    data.pop("uri", None)
    return data
