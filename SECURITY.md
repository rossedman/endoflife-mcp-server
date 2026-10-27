# Security policy

## Supported versions

Only the latest release of endoflife-mcp-server on [PyPI](https://pypi.org/project/endoflife-mcp-server/) gets security fixes. Upgrade with `uv tool upgrade endoflife-mcp-server`, or let `uvx endoflife-mcp-server` pick up the newest release.

## What counts

The server runs on your machine, inside your MCP client, and passes text from a language model into requests to endoflife.date. Please report anything that could let that input, or a response from the API, do more than it should. For example:

- a tool argument that escapes its URL path segment or reaches a host other than the configured API
- output from the server that corrupts the MCP stdio stream or injects instructions into tool results
- the streamable-http transport accepting connections or requests it should refuse
- a GitHub Actions workflow in this repo that is open to injection or credential theft, or a release asset that can't be verified as described below

Wrong or outdated end-of-life data comes from endoflife.date itself. Report that [upstream](https://github.com/endoflife-date/endoflife.date/issues).

## Reporting a vulnerability

Do not open a public issue. Report it privately through GitHub's private vulnerability reporting:

**<https://github.com/rossedman/endoflife-mcp-server/security/advisories/new>**

Include the version (`endoflife-mcp-server --version`), what an attacker could do, and the tool call or steps that reproduce it.

## What to expect

- An acknowledgement within 3 business days.
- A fix, or a plan with a timeline, within 30 days.
- Credit in the published advisory, unless you would rather stay anonymous.

## Verifying releases

Every release is built by [`.github/workflows/release.yml`](https://github.com/rossedman/endoflife-mcp-server/blob/main/.github/workflows/release.yml) and published to PyPI with trusted publishing, so no API tokens are involved. The wheel, the sdist and a `SHA256SUMS` file are attached to each [GitHub release](https://github.com/rossedman/endoflife-mcp-server/releases), each with a keyless [Sigstore](https://www.sigstore.dev/) signature bundle (`<file>.sigstore.json`) and a build provenance attestation.

Download a file and its bundle from the release, then check that the release workflow in this repository signed it:

```sh
cosign verify-blob endoflife_mcp_server-1.0.0-py3-none-any.whl \
  --bundle endoflife_mcp_server-1.0.0-py3-none-any.whl.sigstore.json \
  --certificate-identity-regexp '^https://github.com/rossedman/endoflife-mcp-server/.github/workflows/release.yml@refs/tags/v' \
  --certificate-oidc-issuer https://token.actions.githubusercontent.com
```

Check the downloads against the signed checksums, and check where they were built:

```sh
sha256sum --ignore-missing -c SHA256SUMS
gh attestation verify endoflife_mcp_server-1.0.0-py3-none-any.whl --repo rossedman/endoflife-mcp-server
```

Replace `1.0.0` with the version you downloaded.
