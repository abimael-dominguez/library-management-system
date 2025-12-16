#!/bin/bash
set -e

PROFILE="${1:-immersion}"
REGION="${2:-us-east-1}"

echo "🧹 Limpiando recursos de AWS..."
echo "Profile: $PROFILE"
echo "Region: $REGION"
echo ""
read -p "¿Estás seguro? Esto eliminará TODOS los recursos (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    echo "Cancelado."
    exit 1
fi

ACCOUNT_ID=$(aws sts get-caller-identity --profile $PROFILE --query Account --output text)

# 1. Eliminar API Gateway (primero para desvincular Lambda)
echo "🗑️  Eliminando API Gateway..."
API_ID=$(aws apigateway get-rest-apis --profile $PROFILE --region $REGION --query 'items[?name==`lms-api-dev`].id' --output text)
if [ ! -z "$API_ID" ] && [ "$API_ID" != "None" ]; then
    aws apigateway delete-rest-api --profile $PROFILE --region $REGION --rest-api-id $API_ID
    echo "  ✓ API Gateway eliminado: $API_ID"
else
    echo "  - API Gateway no existe"
fi

# 2. Eliminar funciones Lambda
echo "🗑️  Eliminando funciones Lambda..."
if aws lambda get-function --profile $PROFILE --region $REGION --function-name lms-books-dev &>/dev/null; then
    aws lambda delete-function --profile $PROFILE --region $REGION --function-name lms-books-dev
    echo "  ✓ lms-books-dev eliminado"
else
    echo "  - lms-books-dev no existe"
fi

if aws lambda get-function --profile $PROFILE --region $REGION --function-name lms-loans-dev &>/dev/null; then
    aws lambda delete-function --profile $PROFILE --region $REGION --function-name lms-loans-dev
    echo "  ✓ lms-loans-dev eliminado"
else
    echo "  - lms-loans-dev no existe"
fi

# 3. Eliminar Lambda Layers
echo "🗑️  Eliminando Lambda Layers..."
LAYER_DELETED=false
for version in {1..10}; do
    if aws lambda get-layer-version --profile $PROFILE --region $REGION --layer-name lms-dependencies --version-number $version &>/dev/null; then
        aws lambda delete-layer-version --profile $PROFILE --region $REGION --layer-name lms-dependencies --version-number $version
        LAYER_DELETED=true
    fi
done
if [ "$LAYER_DELETED" = true ]; then
    echo "  ✓ Lambda Layers eliminados"
else
    echo "  - No hay Lambda Layers"
fi

# 4. Vaciar y eliminar bucket S3
echo "🗑️  Vaciando y eliminando bucket S3..."
BUCKET_NAME="lms-static-$ACCOUNT_ID-$REGION"
if aws s3 ls s3://$BUCKET_NAME --profile $PROFILE &>/dev/null; then
    aws s3 rm s3://$BUCKET_NAME --recursive --profile $PROFILE
    echo "  ✓ Bucket vaciado"
    aws s3 rb s3://$BUCKET_NAME --profile $PROFILE
    echo "  ✓ Bucket eliminado"
else
    echo "  - Bucket no existe"
fi

# 5. Eliminar tabla DynamoDB
echo "🗑️  Eliminando tabla DynamoDB..."
if aws dynamodb describe-table --profile $PROFILE --region $REGION --table-name lms-table-dev &>/dev/null; then
    aws dynamodb delete-table --profile $PROFILE --region $REGION --table-name lms-table-dev
    echo "  ✓ lms-table-dev eliminado"
else
    echo "  - lms-table-dev no existe"
fi

# 6. Eliminar roles IAM (al final porque otros recursos lo usan)
echo "🗑️  Eliminando roles IAM..."
ROLE_NAME="lms-lambda-role"
if aws iam get-role --profile $PROFILE --role-name $ROLE_NAME &>/dev/null; then
    aws iam detach-role-policy --profile $PROFILE --role-name $ROLE_NAME --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole 2>/dev/null || true
    aws iam detach-role-policy --profile $PROFILE --role-name $ROLE_NAME --policy-arn arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess 2>/dev/null || true
    aws iam delete-role --profile $PROFILE --role-name $ROLE_NAME
    echo "  ✓ $ROLE_NAME eliminado"
else
    echo "  - $ROLE_NAME no existe"
fi

# 7. Eliminar stacks de CloudFormation (si existen)
echo "🗑️  Eliminando stacks de CloudFormation..."
if aws cloudformation describe-stacks --profile $PROFILE --region $REGION --stack-name lms-serverless &>/dev/null; then
    aws cloudformation delete-stack --profile $PROFILE --region $REGION --stack-name lms-serverless
    echo "  ✓ lms-serverless eliminado"
else
    echo "  - lms-serverless no existe"
fi

if aws cloudformation describe-stacks --profile $PROFILE --region $REGION --stack-name lms-serverless-v2 &>/dev/null; then
    aws cloudformation delete-stack --profile $PROFILE --region $REGION --stack-name lms-serverless-v2
    echo "  ✓ lms-serverless-v2 eliminado"
else
    echo "  - lms-serverless-v2 no existe"
fi

echo ""
echo "✅ Limpieza completada!"
echo ""
echo "Nota: Algunos recursos pueden tardar unos minutos en eliminarse completamente."
echo "Verifica en la consola de AWS que todo se haya eliminado correctamente."
