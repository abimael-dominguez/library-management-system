#!/bin/bash

# LMS Stack Destruction Script
# Usage: ./scripts/destroy.sh [dev|prod]

set -e

ENVIRONMENT=${1:-dev}
PROFILE="immersion"

echo "🗑️  Destroying LMS $ENVIRONMENT environment..."

# Validate environment
if [[ "$ENVIRONMENT" != "dev" && "$ENVIRONMENT" != "prod" ]]; then
    echo "❌ Invalid environment. Use 'dev' or 'prod'"
    exit 1
fi

STACK_NAME="lms-serverless$([ "$ENVIRONMENT" == "prod" ] && echo "-prod" || echo "")"

# Confirmation prompt
echo "⚠️  WARNING: This will permanently delete all resources in stack '$STACK_NAME'"
echo "   - DynamoDB table and all data"
echo "   - Lambda functions"
echo "   - API Gateway"
echo "   - S3 bucket and contents"
echo ""
read -p "Are you sure you want to continue? (type 'yes' to confirm): " confirmation

if [[ "$confirmation" != "yes" ]]; then
    echo "❌ Destruction cancelled"
    exit 1
fi

# Empty S3 bucket first (required before stack deletion)
echo "🗑️  Emptying S3 bucket..."
BUCKET_NAME=$(aws cloudformation describe-stacks \
    --profile $PROFILE \
    --stack-name $STACK_NAME \
    --query 'Stacks[0].Outputs[?OutputKey==`StaticWebsiteBucket`].OutputValue' \
    --output text 2>/dev/null || echo "")

if [[ -n "$BUCKET_NAME" ]]; then
    aws s3 rm s3://$BUCKET_NAME --recursive --profile $PROFILE || true
    echo "✅ S3 bucket emptied"
fi

# Delete CloudFormation stack
echo "🗑️  Deleting CloudFormation stack..."
aws cloudformation delete-stack \
    --profile $PROFILE \
    --stack-name $STACK_NAME

echo "⏳ Waiting for stack deletion to complete..."
aws cloudformation wait stack-delete-complete \
    --profile $PROFILE \
    --stack-name $STACK_NAME

echo "✅ Stack '$STACK_NAME' deleted successfully!"

# Clean up SAM artifacts
echo "🧹 Cleaning up local SAM artifacts..."
rm -rf .aws-sam/
echo "✅ Local cleanup completed"