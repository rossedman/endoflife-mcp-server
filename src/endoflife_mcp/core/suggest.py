"""Suggest product names for a name endoflife.date doesn't know."""

import difflib
from collections.abc import Iterable

from endoflife_mcp.client.models.product_summary import ProductSummary


def suggest_products(
    name: str, products: Iterable[ProductSummary], limit: int = 5, cutoff: float = 0.6
) -> list[str]:
    """Return the canonical names of the products closest to ``name``.

    Both canonical names and aliases are matched, so ``"postgres"`` finds
    ``postgresql`` and a typo such as ``"pyhton"`` finds ``python``. Each product is
    listed at most once, by its canonical name, closest match first.

    Args:
        name: The normalized product name that was not found.
        products: Product summaries from the products list endpoint.
        limit: The most suggestions to return.
        cutoff: The minimum similarity ratio (0 to 1) for a suggestion.

    Returns:
        Up to ``limit`` canonical product names, best match first.
    """
    canonical: dict[str, str] = {}
    for product in products:
        canonical.setdefault(product.name, product.name)
        for alias in product.aliases:
            canonical.setdefault(alias, product.name)
    matches = difflib.get_close_matches(name, canonical, n=len(canonical), cutoff=cutoff)
    suggestions: list[str] = []
    for match in matches:
        product_name = canonical[match]
        if product_name not in suggestions:
            suggestions.append(product_name)
        if len(suggestions) == limit:
            break
    return suggestions
