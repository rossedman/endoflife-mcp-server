# syntax=docker/dockerfile:1
# Runs the MCP server on stdio by default:
#   docker run -i --rm endoflife-mcp-server
# or over HTTP:
#   docker run --rm -p 8000:8000 -e ENDOFLIFE_MCP_TRANSPORT=streamable-http -e ENDOFLIFE_MCP_HOST=0.0.0.0 endoflife-mcp-server

FROM ghcr.io/astral-sh/uv:0.13.6 AS uv

FROM python:3.13-slim-trixie@sha256:b3575dcf816cdacc5292df77a6e3e59b8941631078373a045efa2ac1e9c5c3b2 AS build
COPY --from=uv /uv /bin/uv
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=0
WORKDIR /app

# Dependencies first, so source changes don't invalidate this layer.
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --no-dev

# The version normally comes from git tags; the image has no .git, so pass it in.
ARG VERSION=0.0.0
COPY pyproject.toml uv.lock README.md LICENSE ./
COPY src ./src
RUN --mount=type=cache,target=/root/.cache/uv \
    SETUPTOOLS_SCM_PRETEND_VERSION=${VERSION} uv sync --locked --no-dev --no-editable

FROM python:3.13-slim-trixie@sha256:b3575dcf816cdacc5292df77a6e3e59b8941631078373a045efa2ac1e9c5c3b2
RUN useradd --uid 1000 --no-create-home --shell /usr/sbin/nologin mcp
COPY --from=build --chown=mcp:mcp /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"
USER mcp
ENTRYPOINT ["endoflife-mcp-server"]
CMD ["serve"]
