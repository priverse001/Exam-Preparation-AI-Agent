#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
UV_CACHE_DIR="${UV_CACHE_DIR:-$HOME/.cache/uv}"

ensure_writable_dir() {
    local dir="$1"

    mkdir -p "$dir"

    if [[ -w "$dir" ]]; then
        return 0
    fi

    if command -v sudo >/dev/null 2>&1; then
        sudo chown -R "$(id -u):$(id -g)" "$dir"
    else
        chown -R "$(id -u):$(id -g)" "$dir" 2>/dev/null || true
    fi

    if [[ ! -w "$dir" ]]; then
        echo "Directory is not writable: $dir" >&2
        exit 1
    fi
}

ensure_writable_dir "$PROJECT_DIR/node_modules"
ensure_writable_dir "$PROJECT_DIR/frontend/node_modules"
ensure_writable_dir "$UV_CACHE_DIR"
