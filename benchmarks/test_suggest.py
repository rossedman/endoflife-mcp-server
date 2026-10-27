"""Benchmark product suggestions, which scan every name and alias on a 404."""

from pytest_benchmark.fixture import BenchmarkFixture

from endoflife_mcp.client.models.product_list_response import ProductListResponse
from endoflife_mcp.core.suggest import suggest_products
from tests.conftest import load_fixture

PRODUCTS = ProductListResponse.from_dict(load_fixture("products.json")).result


def test_suggest_for_a_typo(benchmark: BenchmarkFixture) -> None:
    """Suggest names for a typo against the full real product list."""
    assert benchmark(suggest_products, "kubernets", PRODUCTS)[0] == "kubernetes"


def test_suggest_with_no_match(benchmark: BenchmarkFixture) -> None:
    """The worst case: nothing is close, so every candidate is scored."""
    assert benchmark(suggest_products, "qqqqqqqqqqqqqqqq", PRODUCTS) == []
