#!/bin/bash

# Build Lambda Layer Dependencies Script
# This script builds the Lambda layer using Docker to avoid polluting local environment

set -e

echo "🔨 Building Lambda Layer dependencies using Docker..."

# Clean previous build
rm -rf layers/dependencies/python/

# Create python directory
mkdir -p layers/dependencies/python

# Build dependencies using Docker with Python 3.11 (same as Lambda runtime)
docker run --rm \
    -v "$(pwd)/layers/dependencies:/var/task" \
    -w /var/task \
    public.ecr.aws/lambda/python:3.11 \
    pip install -r requirements.txt -t python/ --no-deps

echo "✅ Lambda Layer dependencies built successfully!"
echo "📦 Dependencies installed in: layers/dependencies/python/"