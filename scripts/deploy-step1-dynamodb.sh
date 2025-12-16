#!/bin/bash
set -e

PROFILE="immersion"
REGION="us-east-1"
TABLE_NAME="lms-table-dev"

echo "🗄️  Paso 1: Creando DynamoDB..."

aws dynamodb create-table \
    --profile $PROFILE \
    --region $REGION \
    --table-name $TABLE_NAME \
    --attribute-definitions \
        'AttributeName=pk,AttributeType=S' \
        'AttributeName=sk,AttributeType=S' \
        'AttributeName=gsi1pk,AttributeType=S' \
        'AttributeName=gsi1sk,AttributeType=S' \
    --key-schema \
        'AttributeName=pk,KeyType=HASH' \
        'AttributeName=sk,KeyType=RANGE' \
    --global-secondary-indexes \
        'IndexName=GSI1,KeySchema=[{AttributeName=gsi1pk,KeyType=HASH},{AttributeName=gsi1sk,KeyType=RANGE}],Projection={ProjectionType=ALL}' \
    --billing-mode PAY_PER_REQUEST

echo "✅ DynamoDB creado: $TABLE_NAME"
echo ""
echo "🧪 Verificando instalación..."
aws dynamodb describe-table --profile $PROFILE --region $REGION --table-name $TABLE_NAME --query 'Table.[TableName,TableStatus,ItemCount]' --output table
echo "✅ Verificación exitosa"