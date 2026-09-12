---
name: engineering-mcp
description: Set up and verify this repository's engineering MCP server, including Codex CLI registration and read-only Kubernetes tools.
---

# Engineering MCP

Use this skill when asked to start, connect, or test the MCP server in this repository. Read `server.py` and `README.md` first so the instructions follow the current tool names and configuration.

## Runtime and startup

- The project requires Python 3.10 or newer and pins the MCP SDK to v2 in `pyproject.toml`. Check the environment with `uv run python --version` and install the locked dependencies with `uv sync --locked` when needed.
- The server uses stdio. `uv run server.py` normally prints no success banner and waits for a client; silence by itself is expected. Stop a manually launched process with Ctrl+C. For a real test, let an MCP host launch the server rather than leaving a second copy running in a terminal.
- `codex mcp list` reports the MCP servers configured for the current Codex CLI. If this server is absent, explain that it must be registered before Codex can see it. The stdio registration command is:

  ```bash
  codex mcp add engineering -- uv --directory /absolute/path/to/mcp-demo run server.py
  ```

  Codex also supports environment values on registration with `--env KEY=VALUE`. Use `MCP_ALLOWED_NAMESPACES` when the user wants access to namespaces beyond the default `default`. Do not silently overwrite an existing Codex entry; inspect it and explain the required update first.

## Verify tool discovery and calls

1. Confirm the server appears in `codex mcp list`. In an interactive Codex session, use `/mcp` to confirm it is active and inspect the tools.
2. Start with `search_runbooks(problem: "database connection timeout")` for a tool call that does not need Kubernetes. An absent `runbooks/` directory produces a message but still confirms the tool call completed.
3. Before exercising Kubernetes tools, check `kubectl config current-context` and the target namespace/deployment using `kubectl`. The server uses the current local Kubernetes context and allows only namespaces in `MCP_ALLOWED_NAMESPACES` (default: `default`).
4. Test pod discovery with `get_pods(namespace: "default")`, or the requested allowed namespace.
5. Test log search with `search_logs(service: "<existing-deployment>", query: "ERROR", namespace: "default")`. `namespace` is optional and defaults to `default`; the service must be a single deployment name. The server reads at most the latest 500 deployment log lines and filters them by a case-insensitive substring.

If a tool fails, distinguish a server/transport startup failure from an expected Kubernetes failure such as a missing context, namespace, deployment, or `kubectl` executable. Do not claim a successful infrastructure test based only on the server starting or listing tools. Report the actual tool result, including when no log lines match.
