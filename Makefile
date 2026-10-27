# Every target runs through uv, so the locked environment is always the one used.
CLIENT_DIR := src/endoflife_mcp/client
OPENAPI_CLIENT := openapi-python-client@0.29.1

.PHONY: sync lint fmt type test cover bench fuzz generate generate-check spec-lint docs docs-build docs-serve build check

sync:
	uv sync --locked --all-groups

lint: spec-lint
	uv run ruff check
	uv run ruff format --check
	uv run interrogate src tools
	uv run python tools/check_cmds.py

fmt:
	uv run ruff check --fix
	uv run ruff format

type:
	uv run mypy

test:
	uv run pytest

cover:
	uv run pytest --cov-report=html

bench:
	uv run pytest benchmarks --no-cov --benchmark-autosave --benchmark-compare --benchmark-compare-fail=mean:10%

fuzz:
	uv run pytest tests -m fuzz --no-cov --hypothesis-profile=deep

spec-lint:
	uv run openapi-spec-validator api/external/endoflife.yaml

# Regenerate the endoflife.date client from the vendored OpenAPI spec.
generate:
	uvx $(OPENAPI_CLIENT) generate --path api/external/endoflife.yaml --config openapi-client.yaml \
		--meta none --output-path $(CLIENT_DIR) --overwrite

# Fails when the committed client is stale: regenerating must leave the tree unchanged.
generate-check: generate
	@test -z "$$(git status --porcelain -- $(CLIENT_DIR))" || \
		{ git status --short -- $(CLIENT_DIR); echo "Generated client is stale: run make generate"; exit 1; }

docs:
	@echo "No generated reference pages yet."

docs-build: docs
	uv run --group docs mkdocs build --strict

docs-serve: docs
	uv run --group docs mkdocs serve

build:
	rm -rf dist
	uv build
	uvx twine check dist/*

check: sync lint type generate-check test docs-build build
	uv run pytest benchmarks --no-cov --benchmark-disable
	uv run pytest tests -m fuzz --no-cov --hypothesis-profile=ci
