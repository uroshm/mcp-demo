# Engineering MCP server

This is a small agent-facing [Model Context Protocol](https://modelcontextprotocol.io/) server. It does not contain an LLM or custom agent loop: an MCP-capable host such as ChatGPT, Claude, or VS Code provides the reasoning and invokes these capabilities.

## Capabilities

- `run_tests(module)`: run `pytest` for a path inside the configured test root.

## Run locally

Python 3.10+ is required by the MCP SDK.

```bash
uv run server.py
```

## Inspect with the MCP Inspector

The official [MCP Inspector](https://github.com/modelcontextprotocol/inspector) provides a browser UI for connecting to this stdio server, listing its tools, and trying calls. It requires Node.js 22.19 or newer and `uv`.

Launch it with:

```bash
./scripts/inspect-mcp.sh
```

The first run downloads the Inspector through `npx`; it then prints the local URL to open in a browser. The Inspector launches `uv run server.py` from this checkout. To configure the test root for `run_tests`, export `MCP_TEST_ROOT` before launching:

```bash
MCP_TEST_ROOT=/absolute/path/to/project ./scripts/inspect-mcp.sh
```

For a direct stdio launch, configure the test root before connecting:

```bash
export MCP_TEST_ROOT=/absolute/path/to/project
uv run server.py
```

## Configure an MCP host

```json
{
  "mcpServers": {
    "engineering": {
      "command": "uv",
      "args": ["--directory", "/absolute/path/to/mcp-demo", "run", "server.py"],
      "env": {
        "MCP_TEST_ROOT": "/absolute/path/to/project"
      }
    }
  }
}
```
