#!/bin/sh
set -eu

repo_root=$(CDPATH= cd "$(dirname "$0")/.." && pwd)

exec npx --yes @modelcontextprotocol/inspector \
  --cwd "$repo_root" \
  uv run server.py
