#!/bin/bash
set -e

PROFILE="immersion"
REGION="us-east-1"
ACCOUNT_ID=$(aws sts get-caller-identity --profile $PROFILE --region $REGION --query Account --output text)
BUCKET_NAME="lms-static-$ACCOUNT_ID-$REGION"

echo "📤 Paso 5: Subiendo frontend a S3..."

# Subir archivos
aws s3 sync frontend/src/ s3://$BUCKET_NAME/ --profile $PROFILE --delete

echo "✅ Frontend subido"
echo "🌐 URL: http://$BUCKET_NAME.s3-website-$REGION.amazonaws.com"
