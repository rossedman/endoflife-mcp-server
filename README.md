

```bash
brew install uv
uv venv
source .venv/bin/activate
uv add "mcp[cli]" httpx
```

```json
"endoflife": {
    "command": "uv",
    "args": [
        "--directory",
        "/Users/redman/Code/github.com/rossedman/endoflife-mcp-server",
        "run",
        "endoflife.py"
    ]
},
```