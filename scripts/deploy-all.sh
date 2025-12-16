#!/bin/bash
set -e

echo "🚀 Desplegando Library Management System completo..."
echo ""

# Paso 1: DynamoDB
./scripts/deploy-step1-dynamodb.sh
echo ""

# Paso 2: Seed Data
./scripts/deploy-step2-seed.sh
echo ""

# Paso 3: S3
./scripts/deploy-step3-s3.sh
echo ""

# Paso 4: Lambda
./scripts/deploy-step4-lambda.sh
echo ""

# Paso 5: API Gateway
./scripts/deploy-step5-api.sh
echo ""

# Obtener API URL para actualizar frontend
PROFILE="immersion"
REGION="us-east-1"
API_ID=$(aws apigateway get-rest-apis --profile $PROFILE --region $REGION --query 'items[?name==`lms-api-dev`].id' --output text)
API_URL="https://$API_ID.execute-api.$REGION.amazonaws.com/dev"

echo ""
echo "⚠️  IMPORTANTE: Actualiza el API_BASE_URL en frontend/src/app.js"
echo "   Cambia a: $API_URL"
echo ""
read -p "Presiona Enter cuando hayas actualizado el archivo..."

# Paso 6: Frontend
./scripts/deploy-step6-frontend.sh
echo ""

ACCOUNT_ID=$(aws sts get-caller-identity --profile $PROFILE --region $REGION --query Account --output text)
BUCKET_NAME="lms-static-$ACCOUNT_ID-$REGION"

echo "✅ ¡Despliegue completo!"
echo ""
echo "📋 Recursos creados:"
echo "   - DynamoDB: lms-table-dev"
echo "   - S3: $BUCKET_NAME"
echo "   - Lambda: lms-books-dev"
echo "   - API Gateway: $API_ID"
echo ""
echo "🌐 URLs:"
echo "   - Frontend: http://$BUCKET_NAME.s3-website-$REGION.amazonaws.com"
echo "   - API: $API_URL"
echo ""
echo "📊 Siguiente paso: Cargar datos con Docker"
echo "   docker-compose up -d"
echo "   docker exec -it lms-seed python /app/seed_dynamodb.py"
