# Getting started

Install endoflife-mcp-server, connect it to your AI assistant, and ask your first end-of-life question. You need [uv](https://docs.astral.sh/uv/) and nothing else: it fetches Python 3.11 or newer for you.

## Run it

`uvx` downloads the package from PyPI into a cached environment and runs it. Nothing is installed globally.

```sh
uvx endoflife-mcp-server serve
```

The server speaks MCP over stdio, so it waits silently for a client. Press Ctrl+C to stop it. To see what is available without starting it:

```sh
uvx endoflife-mcp-server --help
uvx endoflife-mcp-server --version
```

To keep a fixed copy on your `PATH` instead, use `uv tool install endoflife-mcp-server`. Then the command is `endoflife-mcp-server serve`, and `uv tool upgrade endoflife-mcp-server` updates it.

## Add it to your assistant

=== "Claude Code"

    ```sh
    claude mcp add -s user endoflife -- uvx endoflife-mcp-server serve
    ```

    `-s user` makes it available in every project. Use `-s project` to share it with your team through `.mcp.json`. Check that it connected with `claude mcp list`, or run `/mcp` inside a session.

=== "Claude Desktop"

    Open **Settings > Developer > Edit Config** and add the server to `claude_desktop_config.json`:

    ```json
    {
      "mcpServers": {
        "endoflife": {
          "command": "uvx",
          "args": ["endoflife-mcp-server", "serve"]
        }
      }
    }
    ```

    Restart Claude Desktop. If it cannot find `uvx`, give the full path from `which uvx` as the `command`.

=== "Other MCP clients"

    Any client that can launch a stdio server works. Give it this command and no environment:

    ```json
    {
      "command": "uvx",
      "args": ["endoflife-mcp-server", "serve"]
    }
    ```

    The key names differ between clients (`mcpServers`, `servers`, `context_servers`), but the command and arguments are always these.

## Ask a question

Once connected, ask in plain language. The assistant picks the tools; see [Using the tools](tools.md) for what it calls and what comes back.

> Is Python 3.10 still supported, and which version should I move to?

> Which Kubernetes versions are still supported, and how long does Amazon EKS keep each one?

## Serve over HTTP

For a client that connects over the network, or to share one server between several people, use the streamable HTTP transport:

```sh
uvx endoflife-mcp-server serve --transport streamable-http --host 127.0.0.1 --port 8000
```

The MCP endpoint is `http://127.0.0.1:8000/mcp`. With Claude Code:

```sh
claude mcp add --transport http endoflife http://127.0.0.1:8000/mcp
```

!!! warning "There is no authentication"
    The server has no login. Keep the default `127.0.0.1` so only your machine can reach it. If you bind `0.0.0.0`, put it behind something that authenticates, such as a reverse proxy or a private network. The data is public, but every connection spends your outbound requests to endoflife.date.

Every option can also come from an environment variable or a config file. See [Configuration](configuration.md).

## Next steps

- [Configuration](configuration.md): timeouts, a mirror of the API, and the config file.
- [Using the tools](tools.md): all eight tools with real output.
- [How it works](how-it-works.md): what happens between your question and the answer.
