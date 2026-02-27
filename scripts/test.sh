#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"

echo "🧪 Running Library Management System Tests"
echo "=========================================="

# Verify Docker daemon/socket access before running compose commands
if ! docker info >/dev/null 2>&1; then
    echo ""
    echo "❌ Docker is not accessible by the current user."
    echo "   Fix options:"
    echo "   1. Start Docker daemon/service"
    echo "   2. Add your user to the docker group and re-login:"
    echo "      sudo usermod -aG docker \$USER"
    echo "      newgrp docker"
    echo "   3. Then rerun: ./scripts/test.sh"
    exit 1
fi

# Build and run tests in Docker
echo "Building test environment..."
# docker-compose build test  # v1
docker compose build test

echo ""
echo "Running unit tests with coverage..."
# docker-compose run --rm test  # v1
docker compose run --rm test

# Check if coverage report was generated
if [ -d "htmlcov" ]; then
    echo ""
    echo "✅ Coverage report generated in htmlcov/ directory"
    echo "📊 Open htmlcov/index.html in your browser to view detailed coverage"
else
    echo "⚠️  Coverage report not generated"
fi

echo ""
echo "🎉 Tests completed!"
echo ""
echo "Next steps:"
echo "1. Review test results and coverage report"
echo "2. Fix any failing tests"
echo "3. If all tests pass, proceed with deployment using ./scripts/deploy.sh"
