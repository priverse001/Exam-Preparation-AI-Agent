#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FAILURES=0
WARNINGS=0
REQUIRED_NODE_MAJOR=22
REQUIRED_NPM_MAJOR=9
REQUIRED_PYTHON_MAJOR=3
REQUIRED_PYTHON_MINOR=11

ok() {
    printf '[ok] %s\n' "$1"
}

warn() {
    printf '[warn] %s\n' "$1"
    WARNINGS=$((WARNINGS + 1))
}

fail() {
    printf '[fail] %s\n' "$1"
    FAILURES=$((FAILURES + 1))
}

check_command() {
    local cmd="$1"
    local label="$2"
    if command -v "$cmd" >/dev/null 2>&1; then
        ok "$label: $(command -v "$cmd")"
    else
        fail "$label not found"
    fi
}

check_optional_command() {
    local cmd="$1"
    local label="$2"
    if command -v "$cmd" >/dev/null 2>&1; then
        ok "$label: $("$cmd" --version 2>/dev/null | head -n 1)"
    else
        warn "$label not found on host (this is fine if you will use the devcontainer)"
    fi
}

version_ge() {
    local current="$1"
    local minimum="$2"
    local current_major current_minor current_patch
    local minimum_major minimum_minor minimum_patch

    IFS=. read -r current_major current_minor current_patch <<<"$current"
    IFS=. read -r minimum_major minimum_minor minimum_patch <<<"$minimum"

    current_patch="${current_patch:-0}"
    minimum_patch="${minimum_patch:-0}"

    if (( current_major > minimum_major )); then
        printf '1'
        return
    fi
    if (( current_major < minimum_major )); then
        printf '0'
        return
    fi
    if (( current_minor > minimum_minor )); then
        printf '1'
        return
    fi
    if (( current_minor < minimum_minor )); then
        printf '0'
        return
    fi
    if (( current_patch >= minimum_patch )); then
        printf '1'
    else
        printf '0'
    fi
}

check_docker_compose() {
    if docker compose version >/dev/null 2>&1; then
        ok "Docker Compose plugin: $(docker compose version | head -n 1)"
    else
        fail "Docker Compose plugin is not available. Install or enable 'docker compose'."
    fi
}

check_optional_node_version() {
    if ! command -v node >/dev/null 2>&1; then
        warn "Node.js not found on host. This is fine for the devcontainer path but required for local setup."
        return 0
    fi

    local version major
    version="$(node --version 2>/dev/null || true)"
    major="$(printf '%s' "$version" | sed -E 's/^v([0-9]+).*/\1/')"

    if [[ -n "$major" ]] && [[ "$major" -lt "$REQUIRED_NODE_MAJOR" ]]; then
        warn "Node.js host version is $version. This project pins Node $REQUIRED_NODE_MAJOR in .nvmrc and the devcontainer."
    else
        ok "Node.js version is suitable for local setup: $version"
    fi
}

check_optional_npm_version() {
    if ! command -v npm >/dev/null 2>&1; then
        warn "npm not found on host. This is fine for the devcontainer path but required for local setup."
        return 0
    fi

    local version major
    version="$(npm --version 2>/dev/null || true)"
    major="$(printf '%s' "$version" | sed -E 's/^([0-9]+).*/\1/')"

    if [[ -n "$major" ]] && [[ "$major" -lt "$REQUIRED_NPM_MAJOR" ]]; then
        warn "npm host version is $version. Use npm $REQUIRED_NPM_MAJOR+ for local setup."
    else
        ok "npm version is suitable for local setup: $version"
    fi
}

check_optional_python_version() {
    local python_cmd=""
    if command -v python3 >/dev/null 2>&1; then
        python_cmd="python3"
    elif command -v python >/dev/null 2>&1; then
        python_cmd="python"
    else
        warn "Python 3.11+ not found on host. This is fine for the devcontainer path but required for local setup."
        return 0
    fi

    local version
    version="$("$python_cmd" -c 'import sys; print(".".join(map(str, sys.version_info[:3])))' 2>/dev/null || true)"

    if [[ -z "$version" ]]; then
        warn "Could not determine Python version from $python_cmd."
        return 0
    fi

    if [[ "$(version_ge "$version" "$REQUIRED_PYTHON_MAJOR.$REQUIRED_PYTHON_MINOR.0")" == "1" ]]; then
        ok "Python version is suitable for local setup: $version ($python_cmd)"
    else
        warn "Python host version is $version via $python_cmd. Use Python $REQUIRED_PYTHON_MAJOR.$REQUIRED_PYTHON_MINOR+ for local setup."
    fi
}

check_optional_uv() {
    if command -v uv >/dev/null 2>&1; then
        ok "uv: $(uv --version 2>/dev/null | head -n 1)"
    else
        warn "uv not found on host. This is fine for the devcontainer path but required for local setup."
    fi
}

printf 'Workshop preflight for %s\n\n' "$PROJECT_DIR"

printf 'Recommended devcontainer host requirements:\n'
check_command git "Git"
check_command docker "Docker CLI"

if docker info >/dev/null 2>&1; then
    ok "Docker daemon is running"
else
    fail "Docker daemon is not reachable. Start Docker Desktop or Docker Engine."
fi
check_docker_compose

printf '\nOptional local setup checks:\n'
check_optional_node_version
check_optional_npm_version
check_optional_python_version
check_optional_uv

if [[ -f "$PROJECT_DIR/.env" ]]; then
    ok ".env file exists"
    if rg '^OPENAI_API_KEY=.+' "$PROJECT_DIR/.env" >/dev/null 2>&1; then
        ok "OPENAI_API_KEY is set in .env"
    else
        warn "OPENAI_API_KEY is missing in .env"
    fi
else
    warn ".env file missing. Run ./workshop/init_env.sh first."
fi

if command -v code >/dev/null 2>&1; then
    ok "VS Code command available"
elif command -v cursor >/dev/null 2>&1; then
    ok "Cursor command available"
else
    warn "No 'code' or 'cursor' command found. This is fine if you open the IDE manually."
fi

printf '\n'
if [[ "$FAILURES" -eq 0 ]]; then
    printf 'Preflight passed with %s warning(s).\n' "$WARNINGS"
    printf 'Next steps:\n'
    printf '  1. For the recommended path, open the repo in your editor and reopen in the devcontainer.\n'
    printf '  2. For local setup, make sure Node %s, npm %s+, Python %s.%s+, and uv are installed.\n' "$REQUIRED_NODE_MAJOR" "$REQUIRED_NPM_MAJOR" "$REQUIRED_PYTHON_MAJOR" "$REQUIRED_PYTHON_MINOR"
    printf '  3. Run ./workshop/init_env.sh and add OPENAI_API_KEY to .env if needed.\n'
    printf '  4. Run npm run start, then ./workshop/healthcheck.sh.\n'
    exit 0
fi

printf 'Preflight failed with %s issue(s) and %s warning(s).\n' "$FAILURES" "$WARNINGS"
exit 1
