"""Contract tests: the recorded responses match the vendored endoflife.date OpenAPI spec.

The service tests use the recorded responses as stand-ins for the real API. These
tests prove the stand-ins are faithful to the spec the client is generated from, so a
green suite means the client, the spec and the fixtures all agree.
"""

from pathlib import Path
from typing import Any

import pytest
import yaml
from openapi_schema_validator import OAS31Validator
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

from tests.conftest import ROUTES, load_fixture

SPEC_PATH = Path(__file__).parents[1] / "api" / "external" / "endoflife.yaml"
SPEC: dict[str, Any] = yaml.safe_load(SPEC_PATH.read_text(encoding="utf-8"))
# OpenAPI 3.1 schemas are JSON Schema 2020-12; the spec itself doesn't say so in $schema.
REGISTRY: Registry = Registry().with_resource(
    SPEC_PATH.as_uri(), Resource.from_contents(SPEC, default_specification=DRAFT202012)
)

# Recorded paths mapped to the spec's path templates.
TEMPLATES = {
    "/products": "/products",
    "/products/python": "/products/{product}",
    "/products/python/releases/3.12": "/products/{product}/releases/{release}",
    "/products/python/releases/latest": "/products/{product}/releases/latest",
    "/categories": "/categories",
    "/categories/os": "/categories/{category}",
    "/tags": "/tags",
    "/tags/linux-distribution": "/tags/{tag}",
}


def response_schema(template: str) -> dict[str, Any]:
    """Return the 200 response schema of a GET operation, as a ``$ref`` into the spec.

    Args:
        template: The spec's path template.

    Returns:
        A schema that refers to the operation's response schema.
    """
    pointer = template.replace("~", "~0").replace("/", "~1")
    response = f"paths/{pointer}/get/responses/200/content/application~1json/schema"
    return {"$ref": f"{SPEC_PATH.as_uri()}#/{response}"}


def test_every_route_has_a_template() -> None:
    """Every recorded route is covered by a contract test."""
    assert set(TEMPLATES) == set(ROUTES)


@pytest.mark.parametrize(("path", "template"), sorted(TEMPLATES.items()))
def test_recorded_response_matches_spec(path: str, template: str) -> None:
    """The recorded response validates against the spec's response schema."""
    validator = OAS31Validator(response_schema(template), registry=REGISTRY)
    errors = sorted(validator.iter_errors(load_fixture(ROUTES[path])), key=str)
    assert not errors, "\n".join(error.message for error in errors[:5])


def test_contract_rejects_a_bad_response() -> None:
    """The validator really checks: a release without its required dates fails."""
    template = "/products/{product}/releases/{release}"
    validator = OAS31Validator(response_schema(template), registry=REGISTRY)
    bad = load_fixture("release_python_3.12.json")
    del bad["result"]["eolFrom"]
    assert not validator.is_valid(bad)
