#!/usr/bin/env bash
set -euo pipefail

BACKEND_URL="${1:-http://localhost:8002/exam-assistant/health}"
FRONTEND_URL="${2:-http://localhost:5173}"
FAILURES=0

ok() {
    printf '[ok] %s\n' "$1"
}

fail() {
    printf '[fail] %s\n' "$1"
    FAILURES=$((FAILURES + 1))
}

if ! command -v curl >/dev/null 2>&1; then
    echo "curl is required for health checks" >&2
    exit 1
fi

printf 'Workshop app healthcheck\n\n'

if backend_response=$(curl -fsS "$BACKEND_URL" 2>/dev/null); then
    ok "Backend reachable at $BACKEND_URL"
    printf '      response: %s\n' "$backend_response"
else
    fail "Backend not reachable at $BACKEND_URL"
fi

if curl -fsS "$FRONTEND_URL" >/dev/null 2>&1; then
    ok "Frontend reachable at $FRONTEND_URL"
else
    fail "Frontend not reachable at $FRONTEND_URL"
fi

printf '\n'
if [[ "$FAILURES" -eq 0 ]]; then
    printf 'Healthcheck passed.\n'
    printf 'Suggested smoke test: upload resources/documents/CPU.md and ask a question in the browser.\n'
    exit 0
fi

printf 'Healthcheck failed with %s issue(s).\n' "$FAILURES"
exit 1
