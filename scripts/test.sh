#!/bin/bash

# Test Runner Script
# Usage: ./scripts/test.sh [unit|integration|all]

set -e

TEST_TYPE=${1:-all}

echo "🧪 Running tests in Docker environment..."

case $TEST_TYPE in
    unit)
        echo "📋 Running unit tests only..."
        docker build -f Dockerfile.test -t lms-test .
        docker run --rm lms-test pytest tests/unit/ -v --cov=src
        ;;
        
    integration)
        echo "🔗 Running integration tests only..."
        docker build -f Dockerfile.test -t lms-test .
        docker run --rm lms-test pytest tests/integration/ -v --cov=src
        ;;
        
    all)
        echo "🎯 Running all tests..."
        docker build -f Dockerfile.test -t lms-test .
        docker run --rm lms-test pytest tests/ -v --cov=src --cov-report=html
        ;;
        
    *)
        echo "Usage: $0 [unit|integration|all]"
        exit 1
        ;;
esac

echo "✅ Tests completed!"