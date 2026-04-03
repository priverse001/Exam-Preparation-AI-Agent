#!/bin/bash
set -e

echo "Running IIT BHU Workshop Setup Check..."
echo ""

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

if command -v python3 &> /dev/null; then
    cd "$SCRIPT_DIR"
    python3 setup_check.py
elif command -v python &> /dev/null; then
    cd "$SCRIPT_DIR"
    python setup_check.py
else
    echo "ERROR: Python 3 is not installed or not in PATH."
    echo "The setup script needs Python to run, but the workshop itself only requires Docker."
    echo "Install Python 3.11+ or just verify Docker manually: docker compose version"
    exit 1
fi
