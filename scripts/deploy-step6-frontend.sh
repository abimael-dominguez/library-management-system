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
echo ""
echo "🧪 Verificando frontend..."
echo "Archivos en S3:"
aws s3 ls s3://$BUCKET_NAME --profile $PROFILE --region $REGION
echo ""
echo "Probando acceso al sitio:"
curl -s -o /dev/null -w "Status: %{http_code}\n" "http://$BUCKET_NAME.s3-website-$REGION.amazonaws.com"
echo "✅ Verificación exitosa"
