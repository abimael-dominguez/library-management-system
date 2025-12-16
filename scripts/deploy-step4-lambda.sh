#!/bin/bash
set -e

PROFILE="immersion"
REGION="us-east-1"
FUNCTION_NAME="lms-books-dev"

echo "⚡ Paso 4: Creando Lambda function..."

# Verificar si la función ya existe
if aws lambda get-function --profile $PROFILE --region $REGION --function-name $FUNCTION_NAME &>/dev/null; then
    echo "⏭️  Función $FUNCTION_NAME ya existe, saltando..."
    exit 0
fi

# Crear rol IAM para Lambda
ROLE_NAME="lms-lambda-role"
TRUST_POLICY='{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "lambda.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}'

echo "📋 Creando rol IAM..."
aws iam create-role \
    --profile $PROFILE \
    --role-name $ROLE_NAME \
    --assume-role-policy-document "$TRUST_POLICY" \
    --no-cli-pager > /dev/null 2>&1 || echo "Rol ya existe"

# Adjuntar políticas
aws iam attach-role-policy \
    --profile $PROFILE \
    --role-name $ROLE_NAME \
    --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

aws iam attach-role-policy \
    --profile $PROFILE \
    --role-name $ROLE_NAME \
    --policy-arn arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess

# Esperar a que el rol esté disponible
sleep 10

# Crear ZIP del código
echo "📦 Empaquetando código..."
cd src
zip -r ../lambda-function.zip . -x "**/__pycache__/*" "**/*.pyc"
cd ..

# Obtener ARN del rol
ACCOUNT_ID=$(aws sts get-caller-identity --profile $PROFILE --region $REGION --query Account --output text)
ROLE_ARN="arn:aws:iam::$ACCOUNT_ID:role/$ROLE_NAME"

# Crear función Lambda
aws lambda create-function \
    --profile $PROFILE \
    --region $REGION \
    --function-name $FUNCTION_NAME \
    --runtime python3.11 \
    --role $ROLE_ARN \
    --handler application.lambda_handlers.books_handler_cors.lambda_handler \
    --zip-file fileb://lambda-function.zip \
    --environment Variables="{DYNAMODB_TABLE=lms-table-dev,ENVIRONMENT=dev}" \
    --timeout 30 \
    --no-cli-pager > /dev/null

echo "✅ Lambda function creada: $FUNCTION_NAME"
echo ""
echo "🧪 Verificando Lambda..."
aws lambda get-function --profile $PROFILE --region $REGION --function-name $FUNCTION_NAME --query 'Configuration.[FunctionName,Runtime,State]' --output table
echo ""
echo "Probando invocación..."
echo '{"httpMethod":"GET","path":"/books","queryStringParameters":{"limit":"3"}}' > /tmp/lambda-payload.json
STATUS=$(aws lambda invoke --profile $PROFILE --region $REGION --function-name $FUNCTION_NAME --payload file:///tmp/lambda-payload.json /tmp/lambda-test.json --query 'StatusCode' --output text)
echo "Status: $STATUS"
if [ -f /tmp/lambda-test.json ]; then
    BOOK_COUNT=$(cat /tmp/lambda-test.json | jq -r '.body' | jq '.books | length' 2>/dev/null || echo "0")
    echo "Libros devueltos: $BOOK_COUNT"
fi
rm -f /tmp/lambda-test.json /tmp/lambda-payload.json
echo "✅ Verificación exitosa"