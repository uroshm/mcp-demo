---
name: engineering-mcp
description: Set up and verify this repository's engineering MCP server for running tests.
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

  Codex also supports environment values on registration with `--env KEY=VALUE`. Use `MCP_TEST_ROOT` to configure where pytest discovers tests. Do not silently overwrite an existing Codex entry; inspect it and explain the required update first.

## Verify tool discovery and calls

1. Confirm the server appears in `codex mcp list`. In an interactive Codex session, use `/mcp` to confirm it is active and inspect the tools.
2. Test with `run_tests(module: "test_example.py")` to confirm pytest executes successfully.

If a tool fails, distinguish a server/transport startup failure from an expected test failure. Do not claim a successful test run based only on the server starting or listing tools. Report the actual test result.
