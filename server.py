"""A minimal MCP server that runs tests."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

from mcp.server import MCPServer

mcp = MCPServer("engineering-mcp")
MAX_OUTPUT_CHARS = 20_000
COMMAND_TIMEOUT_SECONDS = 30


def _run(command: list[str]) -> str:
    try:
        result = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            timeout=COMMAND_TIMEOUT_SECONDS,
        )
    except FileNotFoundError as exc:
        raise RuntimeError(f"required executable is unavailable: {command[0]}") from exc
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError("command timed out") from exc

    output = (result.stdout or result.stderr).strip()[:MAX_OUTPUT_CHARS]
    if result.returncode != 0:
        raise RuntimeError(output or f"command exited with status {result.returncode}")
    return output


@mcp.tool()
def run_tests(module: str) -> str:
    """Run pytest for a path inside MCP_TEST_ROOT, never an arbitrary command."""
    test_root = Path(os.getenv("MCP_TEST_ROOT", ".")).resolve()
    requested = (test_root / module.strip()).resolve()
    if requested != test_root and test_root not in requested.parents:
        raise ValueError("module must stay inside MCP_TEST_ROOT")
    if not requested.exists():
        raise ValueError("module does not exist inside MCP_TEST_ROOT")
    return _run([os.getenv("MCP_PYTEST_BIN", "pytest"), "-q", str(requested)])


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
