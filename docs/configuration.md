# Configuration

Every setting has a default, a command-line option where it makes sense, an environment variable and a key in an optional TOML file. The defaults work for most people; this page is for when they don't.

## Precedence

When the same setting is given in more than one place, the highest one wins:

1. **Command line**: `serve --port 9000`
2. **Environment variable**: `ENDOFLIFE_MCP_PORT=9000`
3. **Config file**: `port = 9000`
4. **Default**

An option you leave off the command line falls through to the next source, so each place can set a different subset.

## Settings

| Setting | Env var | CLI option | Default | Meaning |
| --- | --- | --- | --- | --- |
| `api_url` | `ENDOFLIFE_MCP_API_URL` | `serve --api-url` | `https://endoflife.date/api/v1` | Base URL of the endoflife.date v1 API. Point it at a mirror or a test server. |
| `timeout` | `ENDOFLIFE_MCP_TIMEOUT` | `serve --timeout` | `10.0` | Seconds to wait for each API request. Must be greater than 0. |
| `transport` | `ENDOFLIFE_MCP_TRANSPORT` | `serve --transport` | `stdio` | `stdio` for local clients, or `streamable-http` to serve over HTTP. |
| `host` | `ENDOFLIFE_MCP_HOST` | `serve --host` | `127.0.0.1` | Address to bind. Only used by `streamable-http`. |
| `port` | `ENDOFLIFE_MCP_PORT` | `serve --port` | `8000` | Port to bind, 1 to 65535. Only used by `streamable-http`. |
| `log_level` | `ENDOFLIFE_MCP_LOG_LEVEL` | none | `WARNING` | `DEBUG`, `INFO`, `WARNING` or `ERROR`, upper case. Logs go to stderr, because stdout carries the protocol. |

There is also one setting about the file itself:

| Env var | CLI option | Meaning |
| --- | --- | --- |
| `ENDOFLIFE_MCP_CONFIG` | `--config`, `-c` | Path of the config file to read. |

`--config` belongs to the root command, so it goes before `serve`:

```sh
endoflife-mcp-server --config ./eol.toml serve --port 9000
```

## The config file

Without `--config`, the server reads `$XDG_CONFIG_HOME/endoflife-mcp-server/config.toml`, which is `~/.config/endoflife-mcp-server/config.toml` when `XDG_CONFIG_HOME` is unset or empty. A missing default file is fine; the server just uses the other sources.

A file you name with `--config` must exist. If it doesn't, the server prints `Error: Config file not found: <path>` and exits with status 2.

Keys are the setting names from the table:

```toml
# ~/.config/endoflife-mcp-server/config.toml
transport = "streamable-http"
host = "127.0.0.1"
port = 9100
timeout = 4.5
log_level = "INFO"
```

Unknown keys are rejected rather than ignored, so a typo fails loudly instead of doing nothing.

## Checking what applies

Suppose the file above, plus `ENDOFLIFE_MCP_PORT=9200` in the environment:

| Command | Port used | Why |
| --- | --- | --- |
| `serve` | `9200` | The environment beats the file. |
| `serve --port 9300` | `9300` | The command line beats both. |
| `serve` with the variable unset | `9100` | Only the file sets it. |

## Validation errors

An invalid value from any source stops the server with a one-line explanation, for example:

```console
$ ENDOFLIFE_MCP_PORT=0 endoflife-mcp-server serve
Error: Invalid value: port: Input should be greater than or equal to 1
```

Values are case-sensitive where they are fixed choices: `ENDOFLIFE_MCP_LOG_LEVEL=debug` is rejected, `DEBUG` is accepted.
