"""A small, security-conscious engineering MCP server."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

from mcp.server import MCPServer


mcp = MCPServer("engineering-mcp")
MAX_OUTPUT_CHARS = 20_000
COMMAND_TIMEOUT_SECONDS = 30


def _allowed_namespaces() -> set[str]:
    return {
        item.strip()
        for item in os.getenv("MCP_ALLOWED_NAMESPACES", "default").split(",")
        if item.strip()
    }


def _require_namespace(namespace: str) -> str:
    namespace = namespace.strip()
    if not namespace or namespace not in _allowed_namespaces():
        raise ValueError("namespace is not in MCP_ALLOWED_NAMESPACES")
    return namespace


def _run(command: list[str]) -> str:
    """Run a fixed executable with no shell and return bounded output."""
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
def get_pods(namespace: str) -> str:
    """List pods in an explicitly allowed Kubernetes namespace."""
    namespace = _require_namespace(namespace)
    return _run([os.getenv("MCP_KUBECTL_BIN", "kubectl"), "get", "pods", "-n", namespace, "-o", "wide"])


@mcp.tool()
def search_logs(service: str, query: str, namespace: str = "default") -> str:
    """Search recent logs for an allowed Kubernetes deployment."""
    namespace = _require_namespace(namespace)
    service, query = service.strip(), query.strip()
    if not service or "/" in service or " " in service:
        raise ValueError("service must be a single deployment name")
    if not query:
        raise ValueError("query must not be empty")
    logs = _run([
        os.getenv("MCP_KUBECTL_BIN", "kubectl"), "logs", f"deployment/{service}",
        "-n", namespace, "--tail=500", "--prefix",
    ])
    matches = [line for line in logs.splitlines() if query.lower() in line.lower()]
    return "\n".join(matches)[:MAX_OUTPUT_CHARS] or f"No log lines matched {query!r}."


@mcp.tool()
def search_runbooks(problem: str) -> str:
    """Search Markdown runbooks under MCP_RUNBOOKS_DIR."""
    problem = problem.strip()
    if not problem:
        raise ValueError("problem must not be empty")
    runbooks_dir = Path(os.getenv("MCP_RUNBOOKS_DIR", "runbooks")).resolve()
    if not runbooks_dir.is_dir():
        return f"Runbook directory does not exist: {runbooks_dir}"
    terms = {term.lower() for term in problem.split() if len(term) > 2}
    results = []
    for path in sorted(runbooks_dir.rglob("*.md")):
        if path.is_file():
            text = path.read_text(encoding="utf-8", errors="replace")
            if not terms or any(term in text.lower() for term in terms):
                results.append(f"## {path.relative_to(runbooks_dir)}\n{text[:4_000]}")
    return "\n\n".join(results)[:MAX_OUTPUT_CHARS] or "No matching runbooks found."


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


@mcp.prompt()
def incident_investigation(service: str) -> str:
    """Provide a reusable read-only investigation sequence for an agent."""
    service = service.strip()
    if not service:
        raise ValueError("service must not be empty")
    return (
        f"Investigate {service}. Start with get_pods, then search_logs for "
        "ERROR and WARN, consult search_runbooks for the observed symptom, "
        "and run only relevant tests. Do not perform write operations."
    )


def main() -> None:
    """Start the MCP server over stdio."""
    mcp.run()


if __name__ == "__main__":
    main()
