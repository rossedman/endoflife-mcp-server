"""Shared fixtures: recorded endoflife.date responses served through a mock transport."""

import json
from collections.abc import AsyncIterator, Callable
from pathlib import Path
from typing import Any

import httpx
import pytest
from hypothesis import HealthCheck, settings

from endoflife_mcp.core.eol import DEFAULT_API_URL, EndOfLife

settings.register_profile("dev", max_examples=100)
settings.register_profile(
    "ci", max_examples=500, deadline=None, suppress_health_check=[HealthCheck.too_slow]
)
settings.register_profile(
    "deep", max_examples=10_000, deadline=None, suppress_health_check=[HealthCheck.too_slow]
)
settings.load_profile("dev")


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    """Skip tests marked ``live`` unless they were selected with ``-m live``.

    Live tests call the real endoflife.date API, so they never run by accident.

    Args:
        config: The pytest config.
        items: The collected tests.
    """
    if "live" in (config.getoption("markexpr") or ""):
        return
    skip = pytest.mark.skip(reason="calls the real API; run with -m live")
    for item in items:
        if "live" in item.keywords:
            item.add_marker(skip)


FIXTURES = Path(__file__).parent / "fixtures"
API_PATH = httpx.URL(DEFAULT_API_URL).path

# Recorded from https://endoflife.date/api/v1 on 2026-10-27.
ROUTES: dict[str, str] = {
    "/products": "products.json",
    "/products/python": "product_python.json",
    "/products/python/releases/3.12": "release_python_3.12.json",
    "/products/python/releases/latest": "release_python_latest.json",
    "/categories": "categories.json",
    "/categories/os": "category_os.json",
    "/tags": "tags.json",
    "/tags/linux-distribution": "tag_linux-distribution.json",
}


def load_fixture(name: str) -> Any:
    """Load a recorded API response.

    Args:
        name: File name in ``tests/fixtures``.

    Returns:
        The parsed JSON.
    """
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def recorded_api(request: httpx.Request) -> httpx.Response:
    """Answer a request from the recorded responses, like endoflife.date would.

    Unknown paths get the HTML 404 page the real API sends.

    Args:
        request: The outgoing request.

    Returns:
        The recorded response, or a 404.
    """
    path = request.url.path.removeprefix(API_PATH)
    fixture = ROUTES.get(path)
    if fixture is None:
        return httpx.Response(404, html="<html><body>Not found</body></html>")
    return httpx.Response(200, content=(FIXTURES / fixture).read_bytes())


Handler = Callable[[httpx.Request], httpx.Response]


@pytest.fixture
def make_service() -> Callable[[Handler], EndOfLife]:
    """Build services that send requests to a handler instead of the network.

    Returns:
        A factory taking a handler and returning an :class:`EndOfLife`.
    """

    def factory(handler: Handler) -> EndOfLife:
        return EndOfLife(transport=httpx.MockTransport(handler))

    return factory


@pytest.fixture
async def service() -> AsyncIterator[EndOfLife]:
    """A service backed by the recorded responses.

    Yields:
        The service, closed after the test.
    """
    async with EndOfLife(transport=httpx.MockTransport(recorded_api)) as eol:
        yield eol
