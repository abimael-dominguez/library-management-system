#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"

echo "Running local Library Management System tests"
echo "============================================"

if ! docker info >/dev/null 2>&1; then
    echo ""
    echo "Docker is not accessible by the current user."
    echo "Start Docker Desktop and rerun ./scripts/test.sh"
    exit 1
fi

echo "Building test environment..."
docker compose build test

echo ""
echo "Running unit and functional tests with coverage..."
docker compose run --rm test

if [ -d "htmlcov" ]; then
    echo ""
    echo "Coverage report generated in htmlcov/"
else
    echo "Coverage report was not generated"
fi

echo ""
echo "Tests completed."
