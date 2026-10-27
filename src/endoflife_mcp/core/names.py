"""Validation for the names that end up in endoflife.date URL paths.

Names come from a model, so they can be anything: mixed case, padded with spaces, or
crafted to escape the path segment they are placed in. Normalizing and checking them
here keeps every request on the endpoint it was meant for.
"""

import re

from endoflife_mcp.core.errors import InvalidNameError

MAX_NAME_LENGTH = 100
"""Longest name accepted. Real endoflife.date names are well under 50 characters."""

_NAME = re.compile(r"[a-z0-9][a-z0-9._+-]*")
_RELEASE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._+-]*")


def normalize_slug(value: str, kind: str = "product") -> str:
    """Normalize a product, category or tag name and check it is a valid slug.

    endoflife.date names are lowercase slugs such as ``python``, ``amazon-eks`` or
    ``linux-distribution``. Surrounding whitespace is stripped and the name is
    lowercased, so ``" Python "`` becomes ``"python"``.

    Args:
        value: The name as given by the caller.
        kind: What the name identifies, used in error messages.

    Returns:
        The normalized name.

    Raises:
        InvalidNameError: If the name is empty, too long, or contains characters that
            never appear in endoflife.date names.
    """
    name = value.strip().lower()
    _check(name, _NAME, kind, "lowercase letters, digits, '.', '_', '+' and '-'")
    return name


def normalize_release(value: str) -> str:
    """Normalize a release cycle name and check it is safe to put in a URL path.

    Release cycles keep their case (some products use names like ``R2`` or ``SP1``), so
    only surrounding whitespace is stripped.

    Args:
        value: The release cycle name as given by the caller, such as ``"3.12"``.

    Returns:
        The normalized release cycle name.

    Raises:
        InvalidNameError: If the name is empty, too long, or contains characters that
            never appear in release cycle names.
    """
    name = value.strip()
    _check(name, _RELEASE, "release", "letters, digits, '.', '_', '+' and '-'")
    return name


def _check(name: str, pattern: re.Pattern[str], kind: str, allowed: str) -> None:
    """Raise :class:`InvalidNameError` unless ``name`` fully matches ``pattern``.

    Args:
        name: The already-normalized name.
        pattern: The pattern a valid name matches in full.
        kind: What the name identifies, used in the error message.
        allowed: A human-readable list of the allowed characters.

    Raises:
        InvalidNameError: If the name does not match or is longer than
            :data:`MAX_NAME_LENGTH`.
    """
    if not name:
        raise InvalidNameError(f"The {kind} name is empty.")
    if len(name) > MAX_NAME_LENGTH:
        raise InvalidNameError(f"The {kind} name is longer than {MAX_NAME_LENGTH} characters.")
    if not pattern.fullmatch(name):
        raise InvalidNameError(
            f"{name!r} is not a valid {kind} name: use {allowed}, starting with a letter or digit."
        )
