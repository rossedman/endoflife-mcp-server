"""Tests for name normalization and validation."""

import re
from urllib.parse import quote

import pytest
from hypothesis import example, given
from hypothesis import strategies as st

from endoflife_mcp.core.errors import InvalidNameError
from endoflife_mcp.core.names import MAX_NAME_LENGTH, normalize_release, normalize_slug


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("python", "python"),
        (" Python ", "python"),
        ("AMAZON-EKS", "amazon-eks"),
        ("dotnet", "dotnet"),
        ("red-hat-build-of-openjdk", "red-hat-build-of-openjdk"),
        ("c++", "c++"),
        ("node.js", "node.js"),
        ("a" * MAX_NAME_LENGTH, "a" * MAX_NAME_LENGTH),
    ],
)
def test_normalize_slug_accepts_real_names(raw: str, expected: str) -> None:
    """Real product, category and tag names normalize to lowercase slugs."""
    assert normalize_slug(raw) == expected


@pytest.mark.parametrize(
    ("raw", "message"),
    [
        ("", "empty"),
        ("   ", "empty"),
        ("../etc/passwd", "not a valid product name"),
        ("python/releases/3.12", "not a valid product name"),
        ("-python", "not a valid product name"),
        (".", "not a valid product name"),
        ("py thon", "not a valid product name"),
        ("python?x=1", "not a valid product name"),
        ("python#frag", "not a valid product name"),
        ("pythön", "not a valid product name"),
        ("a" * (MAX_NAME_LENGTH + 1), "longer than"),
    ],
)
def test_normalize_slug_rejects_unsafe_names(raw: str, message: str) -> None:
    """Names that could leave their path segment, or never exist, are rejected."""
    with pytest.raises(InvalidNameError, match=message):
        normalize_slug(raw)


def test_normalize_slug_names_the_kind_in_errors() -> None:
    """The error message says what kind of name was wrong."""
    with pytest.raises(InvalidNameError, match="category"):
        normalize_slug("bad/category", "category")


@pytest.mark.parametrize(
    ("raw", "expected"),
    [("3.12", "3.12"), (" 1.33 ", "1.33"), ("R2", "R2"), ("2019-lts", "2019-lts"), ("v8", "v8")],
)
def test_normalize_release_keeps_case(raw: str, expected: str) -> None:
    """Release names are stripped but keep their case."""
    assert normalize_release(raw) == expected


@pytest.mark.parametrize("raw", ["", "..", "3.12/../..", "3 12", "3.12%2F"])
def test_normalize_release_rejects_unsafe_names(raw: str) -> None:
    """Release names that could leave their path segment are rejected."""
    with pytest.raises(InvalidNameError):
        normalize_release(raw)


SAFE_SEGMENT = re.compile(r"[A-Za-z0-9][A-Za-z0-9._+-]*")


@pytest.mark.fuzz
@given(st.text())
@example("..")
@example("\x00")
@example("%2e%2e")
@example("İ")  # lowercases to two code points
def test_normalize_slug_output_is_always_a_safe_segment(value: str) -> None:
    """Any accepted name is a lowercase, idempotent, single path segment."""
    try:
        name = normalize_slug(value)
    except InvalidNameError:
        return
    assert SAFE_SEGMENT.fullmatch(name)
    assert name == name.lower()
    assert len(name) <= MAX_NAME_LENGTH
    assert normalize_slug(name) == name
    assert quote(name, safe="") == name.replace("+", "%2B")
    assert name not in {".", ".."}


@pytest.mark.fuzz
@given(st.text())
@example("..")
@example("3.12\n")
def test_normalize_release_output_is_always_a_safe_segment(value: str) -> None:
    """Any accepted release name is a stripped, idempotent, single path segment."""
    try:
        name = normalize_release(value)
    except InvalidNameError:
        return
    assert SAFE_SEGMENT.fullmatch(name)
    assert name == value.strip()
    assert normalize_release(name) == name
    assert "/" not in name
    assert name not in {".", ".."}
