#!/usr/bin/env bash
# Run from Git Bash: bash labs/Lab3/run_tests.sh
# Optional overrides: PYTHON=/path/to/python QUARTUS_BIN=/path/to/quartus/bin
set -euo pipefail
LAB_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
if [[ -z "${PYTHON:-}" ]]; then
  bundled="${USERPROFILE:-$HOME}/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe"
  if [[ -f "$bundled" ]]; then
    PYTHON="$bundled"
  else
    PYTHON=python
  fi
fi
export QUARTUS_BIN="${QUARTUS_BIN:-C:/altera/13.0sp1/quartus/bin64}"
exec "$PYTHON" "$LAB_DIR/Tests/run_tests.py"
