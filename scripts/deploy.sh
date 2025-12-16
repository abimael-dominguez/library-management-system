#!/bin/bash

# LMS Deployment Script
# Usage: ./scripts/deploy.sh [dev|prod]

set -e

ENVIRONMENT=${1:-dev}
PROFILE="immersion"

echo "🚀 Deploying LMS to $ENVIRONMENT environment..."

# Validate environment
if [[ "$ENVIRONMENT" != "dev" && "$ENVIRONMENT" != "prod" ]]; then
    echo "❌ Invalid environment. Use 'dev' or 'prod'"
    exit 1
fi

# Check if SAM CLI is installed
if ! command -v sam &> /dev/null; then
    echo "❌ SAM CLI is not installed. Please install it first."
    echo "   https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html"
    exit 1
fi

# Check AWS profile
if ! aws --profile $PROFILE sts get-caller-identity &> /dev/null; then
    echo "❌ AWS profile '$PROFILE' not configured or invalid"
    exit 1
fi

echo "✅ Using AWS profile: $PROFILE"
echo "✅ Deploying to environment: $ENVIRONMENT"

# Build Lambda Layer dependencies
echo "📦 Building Lambda Layer dependencies..."
./scripts/build-layer.sh

# Build SAM application
echo "🔨 Building SAM application..."
sam build --profile $PROFILE

# Deploy based on environment
if [[ "$ENVIRONMENT" == "dev" ]]; then
    echo "🚀 Deploying to DEV environment..."
    sam deploy --profile $PROFILE --config-env default
else
    echo "🚀 Deploying to PROD environment..."
    sam deploy --profile $PROFILE --config-env prod
fi

# Get outputs
echo "📋 Deployment outputs:"
aws cloudformation describe-stacks \
    --profile $PROFILE \
    --stack-name "lms-serverless$([ "$ENVIRONMENT" == "prod" ] && echo "-prod" || echo "")" \
    --query 'Stacks[0].Outputs[*].[OutputKey,OutputValue]' \
    --output table

echo "✅ Deployment completed successfully!"
echo ""
echo "Next steps:"
echo "1. Upload frontend files to S3 bucket"
echo "2. Seed DynamoDB with initial data: python local/scripts/csv_to_dynamodb.py"
echo "3. Test API endpoints"