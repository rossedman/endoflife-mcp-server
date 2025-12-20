# Alpine-based Dockerfile for size optimization
# Base image is ~73MB vs ~201MB for slim
FROM python:3.13-alpine

# Set working directory
WORKDIR /app

# Install build dependencies needed for Python packages with C extensions
# These are removed after installation to keep image small
RUN apk add --no-cache --virtual .build-deps \
    gcc \
    musl-dev \
    libffi-dev \
    openssl-dev \
    cargo \
    rust && \
    pip install --no-cache-dir uv && \
    apk del .build-deps && \
    apk add --no-cache libffi openssl

# Copy dependency files
COPY pyproject.toml ./

# Install dependencies using uv
RUN apk add --no-cache --virtual .build-deps gcc musl-dev libffi-dev && \
    uv pip install --system --no-cache -e . && \
    apk del .build-deps

# Copy application code
COPY main.py ./
COPY .vulture_whitelist.py* ./

# Create non-root user for security
RUN adduser -D -u 1000 mcp && \
    chown -R mcp:mcp /app

# Switch to non-root user
USER mcp

# Run the MCP server
CMD ["python", "main.py"]
