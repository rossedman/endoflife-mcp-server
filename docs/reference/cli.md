# `endoflife-mcp-server`

An MCP server for endoflife.date: end-of-life and support dates for your AI assistant.

**Usage**:

```console
$ endoflife-mcp-server [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `-c, --config <file>`: Config file (default: $XDG_CONFIG_HOME/endoflife-mcp-server/config.toml).  [env var: ENDOFLIFE_MCP_CONFIG]
* `--version`: Show the version and exit.
* `--help`: Show this message and exit.

**Commands**:

* `serve`: Run the MCP server (stdio by default).
* `version`: Print the installed version.

## `endoflife-mcp-server serve`

Run the MCP server (stdio by default). Unset options fall back to ENDOFLIFE_MCP_* environment variables, then the config file, then the defaults.

**Usage**:

```console
$ endoflife-mcp-server serve [OPTIONS]
```

**Options**:

* `--transport <stdio|streamable-http>`: stdio for local clients such as Claude Code; streamable-http to serve over HTTP.
* `--host <str>`: Address to bind for streamable-http.
* `--port <int>`: Port for streamable-http.
* `--api-url <str>`: Base URL of the endoflife.date v1 API.
* `--timeout <float>`: Seconds to wait for each API request.
* `--help`: Show this message and exit.

## `endoflife-mcp-server version`

Print the installed version.

**Usage**:

```console
$ endoflife-mcp-server version [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.
