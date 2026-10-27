"""Tests for product name suggestions."""

import pytest
from hypothesis import given
from hypothesis import strategies as st

from endoflife_mcp.client.models.product_list_response import ProductListResponse
from endoflife_mcp.client.models.product_summary import ProductSummary
from endoflife_mcp.core.suggest import suggest_products
from tests.conftest import load_fixture

PRODUCTS = ProductListResponse.from_dict(load_fixture("products.json")).result
CANONICAL = {product.name for product in PRODUCTS}


def summary(name: str, *aliases: str) -> ProductSummary:
    """Build a product summary with the given name and aliases.

    Args:
        name: Canonical product name.
        *aliases: Aliases for the product.

    Returns:
        The summary.
    """
    return ProductSummary(
        name=name, label=name, aliases=list(aliases), category="lang", tags=[], uri=""
    )


@pytest.mark.parametrize(
    ("typo", "expected"),
    [("pyhton", "python"), ("kubernets", "kubernetes"), ("postgres-sql", "postgresql")],
)
def test_suggests_the_intended_product_first(typo: str, expected: str) -> None:
    """Common typos suggest the intended product as the best match."""
    assert suggest_products(typo, PRODUCTS)[0] == expected


def test_matches_aliases_but_returns_canonical_names() -> None:
    """An alias match is reported by the product's canonical name, once."""
    products = [summary("postgresql", "postgres", "pg"), summary("mysql")]
    assert suggest_products("postgre", products) == ["postgresql"]


def test_limit_and_cutoff() -> None:
    """At most ``limit`` names are returned, and only above the cutoff."""
    products = [summary(f"product-{i}") for i in range(10)]
    assert len(suggest_products("product-", products, limit=3)) == 3
    assert suggest_products("zzzzzz", products) == []


def test_no_products() -> None:
    """An empty product list gives no suggestions."""
    assert suggest_products("python", []) == []


@pytest.mark.fuzz
@given(st.text(max_size=120), st.integers(min_value=1, max_value=10))
def test_suggestions_are_unique_canonical_names(name: str, limit: int) -> None:
    """Suggestions are always distinct canonical product names, at most ``limit``."""
    suggestions = suggest_products(name, PRODUCTS, limit=limit)
    assert len(suggestions) <= limit
    assert len(set(suggestions)) == len(suggestions)
    assert set(suggestions) <= CANONICAL


@pytest.mark.fuzz
@given(st.sampled_from(sorted(CANONICAL)))
def test_an_exact_name_is_its_own_best_suggestion(name: str) -> None:
    """A canonical name always suggests itself first."""
    assert suggest_products(name, PRODUCTS)[0] == name


def test_canonical_names_win_over_aliases() -> None:
    """A product's own name beats another product's identical alias."""
    products = [summary("openjdk", "java"), summary("java")]
    assert suggest_products("java", products)[0] == "java"
