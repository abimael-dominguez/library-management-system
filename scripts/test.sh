#!/bin/bash

set -e

echo "🧪 Running Library Management System Tests"
echo "=========================================="

# Build and run tests in Docker
echo "Building test environment..."
docker-compose build test

echo ""
echo "Running unit tests with coverage..."
docker-compose run --rm test

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