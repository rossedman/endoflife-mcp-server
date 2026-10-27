"""Benchmark name validation, which runs on every tool call."""

from pytest_benchmark.fixture import BenchmarkFixture

from endoflife_mcp.core.names import normalize_release, normalize_slug
from tests.conftest import load_fixture

NAMES = [product["name"] for product in load_fixture("products.json")["result"]]


def test_normalize_every_product_name(benchmark: BenchmarkFixture) -> None:
    """Normalize all ~500 real product names, padded and upper-cased."""
    padded = [f"  {name.upper()} " for name in NAMES]

    def run() -> list[str]:
        return [normalize_slug(name) for name in padded]

    assert benchmark(run) == NAMES


def test_normalize_release(benchmark: BenchmarkFixture) -> None:
    """Normalize a typical release cycle name."""
    assert benchmark(normalize_release, " 3.12 ") == "3.12"
