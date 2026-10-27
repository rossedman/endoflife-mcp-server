"""Benchmark the service's request path: generated-model parsing and error mapping."""

import asyncio

import httpx
from pytest_benchmark.fixture import BenchmarkFixture

from endoflife_mcp.core.eol import EndOfLife
from tests.conftest import recorded_api


def test_product_list(benchmark: BenchmarkFixture) -> None:
    """Fetch and parse the full products list (~500 summaries) from a mock transport."""
    loop = asyncio.new_event_loop()
    service = EndOfLife(transport=httpx.MockTransport(recorded_api))
    try:
        names = benchmark(lambda: loop.run_until_complete(service.product_names()))
        assert "python" in names
    finally:
        loop.run_until_complete(service.aclose())
        loop.close()


def test_product_details(benchmark: BenchmarkFixture) -> None:
    """Fetch, parse and serialize one product with all its releases."""
    loop = asyncio.new_event_loop()
    service = EndOfLife(transport=httpx.MockTransport(recorded_api))
    try:
        product = benchmark(lambda: loop.run_until_complete(service.product("python")))
        assert product["name"] == "python"
    finally:
        loop.run_until_complete(service.aclose())
        loop.close()
