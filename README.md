# Engineering MCP server

This is a small agent-facing [Model Context Protocol](https://modelcontextprotocol.io/) server. It does not contain an LLM or custom agent loop: an MCP-capable host such as ChatGPT, Claude, or VS Code provides the reasoning and invokes these capabilities.

## Capabilities

- `get_pods(namespace)`: list Kubernetes pods.
- `search_logs(service, query, namespace)`: search recent deployment logs.
- `search_runbooks(problem)`: search Markdown runbooks.
- `run_tests(module)`: run `pytest` for a path inside the configured test root.
- `incident_investigation(service)`: reusable investigation prompt.

The server deliberately has no arbitrary `run_command` tool. Kubernetes namespaces, filesystem paths, output size, and command duration are constrained server-side.

## Run locally

Python 3.10+ is required by the MCP SDK.

```bash
uv run server.py
```

Configure the safety boundary before connecting it to real systems:

```bash
export MCP_ALLOWED_NAMESPACES=default,appointments
export MCP_RUNBOOKS_DIR=/absolute/path/to/runbooks
export MCP_TEST_ROOT=/absolute/path/to/project
uv run server.py
```

The Kubernetes tools use the current `kubectl` context. Override its executable with `MCP_KUBECTL_BIN` if needed.

## Configure an MCP host

```json
{
  "mcpServers": {
    "engineering": {
      "command": "uv",
      "args": ["--directory", "/absolute/path/to/mcp-demo", "run", "server.py"],
      "env": {
        "MCP_ALLOWED_NAMESPACES": "default,appointments",
        "MCP_RUNBOOKS_DIR": "/absolute/path/to/runbooks",
        "MCP_TEST_ROOT": "/absolute/path/to/project"
      }
    }
  }
}
```

For production, add authentication, authorization, audit logging, and approval workflows at the MCP deployment boundary as well as in individual tools.
