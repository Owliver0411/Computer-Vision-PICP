#!/usr/bin/env bash
set -euo pipefail

# Always run from the project root, regardless of the caller's current folder.
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

python code/main.py
