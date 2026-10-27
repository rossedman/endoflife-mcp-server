# Contributing

Thanks for helping. endoflife-mcp-server is a small MCP server, and the bar for changes is that every tool keeps answering correctly, quickly and safely. This page covers how to set up, what `make check` enforces, and how changes get merged.

Questions and ideas go in an [issue](https://github.com/rossedman/endoflife-mcp-server/issues/new/choose). Security problems follow the [security policy](SECURITY.md) instead.

## Set up

You need [uv](https://docs.astral.sh/uv/) and `make`. uv installs the right Python for you.

```sh
git clone https://github.com/rossedman/endoflife-mcp-server.git
cd endoflife-mcp-server
uv sync --all-groups
uv run pre-commit install
```

Run the server from your checkout, and point Claude Code at it:

```sh
uv run endoflife-mcp-server serve --help
claude mcp add -s user endoflife-dev -- uv run --directory "$(pwd)" endoflife-mcp-server serve
```

## Check your work

One command runs everything CI runs:

```sh
make check
```

It runs, in order:

| Step | Command | Fails when |
| --- | --- | --- |
| Lock | `uv sync --locked --all-groups` | `uv.lock` is out of date with `pyproject.toml` |
| Spec | `openapi-spec-validator api/external/endoflife.yaml` | the vendored API spec is invalid |
| Lint | `ruff check`, `ruff format --check` | any lint error or unformatted file |
| Docstrings | `interrogate src tools` | any module, class, function or method lacks a docstring |
| Commands | `python tools/check_cmds.py` | a file in `commands/` defines more or less than one command |
| Types | `mypy` (strict) | any type error |
| Generated client | `make generate-check` | the committed client differs from what the spec generates |
| Tests | `pytest` | a test fails, or branch coverage drops below 90% |
| Benchmarks | `pytest benchmarks --benchmark-disable` | a benchmark errors |
| Fuzz | `pytest tests -m fuzz --hypothesis-profile=ci` | a property fails in 500 examples |
| Docs | `mkdocs build --strict` | a broken link, anchor or nav entry |
| Package | `uv build`, `twine check` | the sdist or wheel is invalid |

`make fmt` fixes formatting and the lint errors ruff can fix on its own.

## Quality bars

- **Coverage:** at least 90% branch coverage of hand-written code. The generated client is excluded. Test behavior, not trivial code, to get there.
- **Docstrings:** every module, class, function and method, public and private, has a Google-style docstring. ruff checks the style; interrogate checks that nothing is missing.
- **Types:** full annotations everywhere, checked by mypy in strict mode.
- **One command per file:** each module in `src/endoflife_mcp/commands/` defines exactly one command. `cli.py` registers them.
- **Spec first:** the endoflife.date client in `src/endoflife_mcp/client/` is generated from `api/external/endoflife.yaml`. Never edit it by hand. To pick up an API change, update the spec from <https://endoflife.date/docs/api/v1/openapi.yml>, run `make generate`, and commit both.
- **Tools are read-only and fail loudly:** tools raise `ToolError` with a message the model can act on, and never print to stdout, because on stdio that stream carries the MCP protocol.
- **Critical paths** (below) have a benchmark in `benchmarks/` and, when they take outside input, a Hypothesis property test marked `@pytest.mark.fuzz`.

## Critical paths

These functions parse untrusted input, run on every tool call, or decide configuration. Changes to them need a benchmark and, where they take external input, a fuzz test.

| Function | Why it's critical | Benchmark | Fuzz test |
| --- | --- | --- | --- |
| `core.names.normalize_slug`, `core.names.normalize_release` | Turn model-supplied text into URL path segments; the only thing between a tool argument and the request path | `benchmarks/test_names.py` | `tests/test_names.py` |
| `core.suggest.suggest_products` | Runs on every unknown product name, scanning about 800 names and aliases | `benchmarks/test_suggest.py` | `tests/test_suggest.py` |
| `core.eol.EndOfLife._call` | Parses every API response through the generated models and maps every failure to an error the model sees | `benchmarks/test_eol.py` | `tests/test_eol.py` |
| `config.load_settings` | Resolves settings from CLI options, the environment and the TOML file, in that order | `benchmarks/test_config.py` | `tests/test_config.py` |

Run `make bench` to save a benchmark run and compare it against your last one; it fails if any mean gets more than 10% slower. `make fuzz` runs the property tests with 10,000 examples each.

## Commits and pull requests

Commit messages and PR titles follow [Conventional Commits](https://www.conventionalcommits.org/). The release changelog is grouped by type.

```text
feat: add a tool that lists products by identifier
fix: keep release names case-sensitive in product_get_cycle
docs: show the Claude Desktop config on the getting started page
build(deps): bump mcp to 2.4.0
```

Pull requests are squash-merged, so the PR title becomes the commit on `main`. Every PR needs a passing CI run and a review from the code owner in [`.github/CODEOWNERS`](.github/CODEOWNERS). Fill in the PR template, keep each PR to one change, and add tests with the change.

## Releases

Maintainers release by pushing a `v*` tag. The version comes from the tag, so nothing needs bumping by hand. The release workflow tests, builds, publishes to PyPI through trusted publishing, signs every file with Sigstore, and creates the GitHub release. See [Verifying releases](SECURITY.md#verifying-releases).

## Code of conduct

Everyone taking part in this project follows the [code of conduct](CODE_OF_CONDUCT.md).
