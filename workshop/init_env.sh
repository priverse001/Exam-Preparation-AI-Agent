#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TEMPLATE="$PROJECT_DIR/.env.template"
TARGET="$PROJECT_DIR/.env"

if [[ ! -f "$TEMPLATE" ]]; then
    echo "Missing template file: $TEMPLATE" >&2
    exit 1
fi

if [[ -f "$TARGET" ]]; then
    echo ".env already exists at $TARGET"
    echo "Leaving it unchanged."
    exit 0
fi

cp "$TEMPLATE" "$TARGET"
echo "Created .env from .env.template"
echo "Next: edit .env and set OPENAI_API_KEY"
