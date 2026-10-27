"""Tests for the endoflife.date service, against recorded and synthetic responses."""

import asyncio
import json
from collections.abc import Callable
from typing import Any

import httpx
import pytest
from hypothesis import given
from hypothesis import strategies as st

from endoflife_mcp.core.eol import USER_AGENT, EndOfLife
from endoflife_mcp.core.errors import (
    EndOfLifeError,
    InvalidNameError,
    NotFoundError,
    RateLimitedError,
    UpstreamError,
)
from tests.conftest import Handler, load_fixture, recorded_api

MakeService = Callable[[Handler], EndOfLife]


async def test_product_names(service: EndOfLife) -> None:
    """The products list is reduced to canonical names, in API order."""
    names = await service.product_names()
    assert names[0] == "adonisjs"
    assert "python" in names
    assert len(names) == load_fixture("products.json")["total"]


async def test_product_returns_details_with_releases(service: EndOfLife) -> None:
    """A product comes back with every release cycle, in the API's camelCase keys."""
    product = await service.product(" Python ")
    assert product["name"] == "python"
    assert product["category"] == "lang"
    cycles = {release["name"]: release for release in product["releases"]}
    assert cycles["3.12"]["eolFrom"] == "2028-10-31"


async def test_release(service: EndOfLife) -> None:
    """One release cycle is returned by name."""
    release = await service.release("python", "3.12")
    assert release == load_fixture("release_python_3.12.json")["result"]


async def test_latest_release(service: EndOfLife) -> None:
    """The latest release cycle is returned."""
    release = await service.latest_release("python")
    assert release["name"] == load_fixture("release_python_latest.json")["result"]["name"]


async def test_categories_and_category_products(service: EndOfLife) -> None:
    """Categories list by name; category products drop the API URL."""
    assert "os" in await service.categories()
    products = await service.category_products("os")
    assert products
    assert all(product["category"] == "os" for product in products)
    assert all("uri" not in product for product in products)


async def test_tags_and_tag_products(service: EndOfLife) -> None:
    """Tags list by name; tag products carry the tag."""
    assert "linux-distribution" in await service.tags()
    products = await service.tag_products("linux-distribution")
    assert all("linux-distribution" in product["tags"] for product in products)


async def test_unknown_product_suggests_close_names(service: EndOfLife) -> None:
    """A 404 for a product lists close product names."""
    with pytest.raises(NotFoundError, match=r"no product 'pyhton'\. Did you mean: python"):
        await service.product("pyhton")


async def test_unknown_product_without_close_names(service: EndOfLife) -> None:
    """A 404 with nothing close says so without suggestions."""
    with pytest.raises(NotFoundError) as info:
        await service.product("zzzzzzzzzz")
    assert str(info.value) == "endoflife.date has no product 'zzzzzzzzzz'."


async def test_unknown_release_of_known_product(service: EndOfLife) -> None:
    """A 404 for a release of a real product doesn't suggest product names."""
    with pytest.raises(NotFoundError) as info:
        await service.release("python", "0.1")
    assert str(info.value) == "endoflife.date has no release '0.1' of product 'python'."


async def test_unknown_category_and_tag(service: EndOfLife) -> None:
    """404s for categories and tags name what was missing."""
    with pytest.raises(NotFoundError, match="no category 'nope'"):
        await service.category_products("nope")
    with pytest.raises(NotFoundError, match="no tag 'nope'"):
        await service.tag_products("nope")


async def test_suggestions_are_best_effort(make_service: MakeService) -> None:
    """If the products list fails too, the 404 message has no suggestions."""

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/products"):
            return httpx.Response(503)
        return httpx.Response(404)

    async with make_service(handler) as eol:
        with pytest.raises(NotFoundError) as info:
            await eol.product("pyhton")
    assert str(info.value) == "endoflife.date has no product 'pyhton'."


async def test_invalid_names_never_reach_the_network(make_service: MakeService) -> None:
    """Invalid names fail before any request is sent."""
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200)

    async with make_service(handler) as eol:
        with pytest.raises(InvalidNameError):
            await eol.product("../../etc")
        with pytest.raises(InvalidNameError):
            await eol.release("python", "../..")
    assert requests == []


@pytest.mark.parametrize(
    ("headers", "message"),
    [({"Retry-After": "30"}, "Retry after 30 seconds"), ({}, "Retry later")],
)
async def test_rate_limited(
    make_service: MakeService, headers: dict[str, str], message: str
) -> None:
    """A 429 becomes a RateLimitedError carrying Retry-After."""
    async with make_service(lambda _: httpx.Response(429, headers=headers)) as eol:
        with pytest.raises(RateLimitedError, match=message) as info:
            await eol.product_names()
    assert info.value.retry_after == headers.get("Retry-After")


@pytest.mark.parametrize("status", [500, 502, 503, 304, 301])
async def test_unexpected_status(make_service: MakeService, status: int) -> None:
    """Any other status is an UpstreamError naming the status."""
    async with make_service(lambda _: httpx.Response(status)) as eol:
        with pytest.raises(UpstreamError, match=f"HTTP {status}"):
            await eol.tags()


async def test_network_error(make_service: MakeService) -> None:
    """A connection failure is an UpstreamError."""

    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection refused", request=request)

    async with make_service(handler) as eol:
        with pytest.raises(UpstreamError, match=r"Could not reach endoflife\.date"):
            await eol.categories()


@pytest.mark.parametrize(
    "body", [b"<html>maintenance</html>", b"{}", b'{"result": 1}', b"[]", b"null"]
)
async def test_malformed_body(make_service: MakeService, body: bytes) -> None:
    """A 200 whose body doesn't match the spec is an UpstreamError, not a crash."""
    async with make_service(lambda _: httpx.Response(200, content=body)) as eol:
        with pytest.raises(UpstreamError, match="does not match its API spec"):
            await eol.product("python")


async def test_requests_identify_the_client(make_service: MakeService) -> None:
    """Requests carry the User-Agent and go to the v1 API path."""
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return recorded_api(request)

    async with make_service(handler) as eol:
        await eol.release("python", "3.12")
    assert seen[0].headers["User-Agent"] == USER_AGENT
    assert str(seen[0].url) == "https://endoflife.date/api/v1/products/python/releases/3.12"


async def test_redirects_are_followed(make_service: MakeService) -> None:
    """Aliases redirect to the canonical product, as the real API does."""

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/products/py"):
            return httpx.Response(301, headers={"Location": "/api/v1/products/python"})
        return recorded_api(request)

    async with make_service(handler) as eol:
        assert (await eol.product("py"))["name"] == "python"


JSON = st.recursive(
    st.none() | st.booleans() | st.integers() | st.floats(allow_nan=False) | st.text(),
    lambda children: st.lists(children) | st.dictionaries(st.text(), children),
    max_leaves=20,
)


def mutate(value: Any, path: list[str | int], replacement: Any) -> Any:
    """Return a copy of ``value`` with the item at ``path`` replaced.

    Args:
        value: Parsed JSON.
        path: Keys and indexes leading to the item; an empty path replaces the root.
        replacement: The new value.

    Returns:
        The modified copy.
    """
    if not path:
        return replacement
    copy = json.loads(json.dumps(value))
    target = copy
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = replacement
    return copy


PRODUCT = load_fixture("product_python.json")
PRODUCT_PATHS: list[list[str | int]] = [
    [],
    ["result"],
    ["result", "name"],
    ["result", "releases"],
    ["result", "releases", 0],
    ["result", "releases", 0, "releaseDate"],
    ["result", "releases", 0, "eolFrom"],
    ["result", "releases", 0, "latest"],
    ["result", "labels"],
    ["generated_at"],
]


@pytest.mark.fuzz
@given(st.sampled_from(PRODUCT_PATHS), JSON)
def test_corrupted_responses_only_raise_service_errors(
    path: list[str | int], replacement: Any
) -> None:
    """Whatever the API sends back, the service returns data or raises EndOfLifeError."""
    body = json.dumps(mutate(PRODUCT, path, replacement)).encode()

    async def run() -> None:
        async with EndOfLife(
            transport=httpx.MockTransport(lambda _: httpx.Response(200, content=body))
        ) as eol:
            try:
                result = await eol.product("python")
            except EndOfLifeError:
                return
            json.dumps(result)  # whatever comes back is JSON-serializable for the MCP result

    asyncio.run(run())


@pytest.mark.fuzz
@given(st.binary(max_size=512))
def test_arbitrary_bytes_only_raise_service_errors(body: bytes) -> None:
    """Non-JSON and truncated bodies are UpstreamErrors."""

    async def run() -> None:
        async with EndOfLife(
            transport=httpx.MockTransport(lambda _: httpx.Response(200, content=body))
        ) as eol:
            with pytest.raises(UpstreamError):
                await eol.release("python", "3.12")

    asyncio.run(run())


@pytest.mark.live
async def test_live_api_matches_the_spec() -> None:
    """The real API still parses with the generated client (run with -m live)."""
    async with EndOfLife() as eol:
        assert "python" in await eol.product_names()
        assert (await eol.latest_release("python"))["isMaintained"] is True
