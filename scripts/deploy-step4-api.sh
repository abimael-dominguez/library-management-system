#!/bin/bash
set -e

PROFILE="immersion"
REGION="us-east-1"
API_NAME="lms-api-dev"
FUNCTION_NAME="lms-books-dev"

echo "🌐 Paso 4: Creando API Gateway..."

# Obtener ARN de la función Lambda
ACCOUNT_ID=$(aws sts get-caller-identity --profile $PROFILE --query Account --output text)
LAMBDA_ARN="arn:aws:lambda:$REGION:$ACCOUNT_ID:function:$FUNCTION_NAME"

# Crear API Gateway
API_ID=$(aws apigateway create-rest-api \
    --profile $PROFILE \
    --region $REGION \
    --name $API_NAME \
    --description "Library Management System API" \
    --endpoint-configuration types=REGIONAL \
    --query 'id' \
    --output text)

echo "✅ API creado: $API_ID"

# Obtener root resource ID
ROOT_ID=$(aws apigateway get-resources \
    --profile $PROFILE \
    --region $REGION \
    --rest-api-id $API_ID \
    --query 'items[0].id' \
    --output text)

# Crear recurso /books
BOOKS_RESOURCE_ID=$(aws apigateway create-resource \
    --profile $PROFILE \
    --region $REGION \
    --rest-api-id $API_ID \
    --parent-id $ROOT_ID \
    --path-part books \
    --query 'id' \
    --output text)

# Crear recurso /search
SEARCH_RESOURCE_ID=$(aws apigateway create-resource \
    --profile $PROFILE \
    --region $REGION \
    --rest-api-id $API_ID \
    --parent-id $ROOT_ID \
    --path-part search \
    --query 'id' \
    --output text)

# Configurar método GET en /books
aws apigateway put-method \
    --profile $PROFILE \
    --region $REGION \
    --rest-api-id $API_ID \
    --resource-id $BOOKS_RESOURCE_ID \
    --http-method GET \
    --authorization-type NONE

aws apigateway put-integration \
    --profile $PROFILE \
    --region $REGION \
    --rest-api-id $API_ID \
    --resource-id $BOOKS_RESOURCE_ID \
    --http-method GET \
    --type AWS_PROXY \
    --integration-http-method POST \
    --uri "arn:aws:apigateway:$REGION:lambda:path/2015-03-31/functions/$LAMBDA_ARN/invocations"

# Configurar método OPTIONS en /books (CORS)
aws apigateway put-method \
    --profile $PROFILE \
    --region $REGION \
    --rest-api-id $API_ID \
    --resource-id $BOOKS_RESOURCE_ID \
    --http-method OPTIONS \
    --authorization-type NONE

aws apigateway put-integration \
    --profile $PROFILE \
    --region $REGION \
    --rest-api-id $API_ID \
    --resource-id $BOOKS_RESOURCE_ID \
    --http-method OPTIONS \
    --type MOCK \
    --request-templates '{"application/json": "{\"statusCode\": 200}"}'

aws apigateway put-method-response \
    --profile $PROFILE \
    --region $REGION \
    --rest-api-id $API_ID \
    --resource-id $BOOKS_RESOURCE_ID \
    --http-method OPTIONS \
    --status-code 200 \
    --response-parameters '{"method.response.header.Access-Control-Allow-Headers":false,"method.response.header.Access-Control-Allow-Methods":false,"method.response.header.Access-Control-Allow-Origin":false}'

aws apigateway put-integration-response \
    --profile $PROFILE \
    --region $REGION \
    --rest-api-id $API_ID \
    --resource-id $BOOKS_RESOURCE_ID \
    --http-method OPTIONS \
    --status-code 200 \
    --response-parameters '{"method.response.header.Access-Control-Allow-Headers":"'\''Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'\''","method.response.header.Access-Control-Allow-Methods":"'\''GET,POST,PUT,DELETE,OPTIONS'\''","method.response.header.Access-Control-Allow-Origin":"'\''*'\''"}' \
    --response-templates '{"application/json": ""}'

# Configurar método GET en /search
aws apigateway put-method \
    --profile $PROFILE \
    --region $REGION \
    --rest-api-id $API_ID \
    --resource-id $SEARCH_RESOURCE_ID \
    --http-method GET \
    --authorization-type NONE \
    --request-parameters '{"method.request.querystring.q":false,"method.request.querystring.limit":false}'

aws apigateway put-integration \
    --profile $PROFILE \
    --region $REGION \
    --rest-api-id $API_ID \
    --resource-id $SEARCH_RESOURCE_ID \
    --http-method GET \
    --type AWS_PROXY \
    --integration-http-method POST \
    --uri "arn:aws:apigateway:$REGION:lambda:path/2015-03-31/functions/$LAMBDA_ARN/invocations"

# Configurar método OPTIONS en /search (CORS)
aws apigateway put-method \
    --profile $PROFILE \
    --region $REGION \
    --rest-api-id $API_ID \
    --resource-id $SEARCH_RESOURCE_ID \
    --http-method OPTIONS \
    --authorization-type NONE

aws apigateway put-integration \
    --profile $PROFILE \
    --region $REGION \
    --rest-api-id $API_ID \
    --resource-id $SEARCH_RESOURCE_ID \
    --http-method OPTIONS \
    --type MOCK \
    --request-templates '{"application/json": "{\"statusCode\": 200}"}'

aws apigateway put-method-response \
    --profile $PROFILE \
    --region $REGION \
    --rest-api-id $API_ID \
    --resource-id $SEARCH_RESOURCE_ID \
    --http-method OPTIONS \
    --status-code 200 \
    --response-parameters '{"method.response.header.Access-Control-Allow-Headers":false,"method.response.header.Access-Control-Allow-Methods":false,"method.response.header.Access-Control-Allow-Origin":false}'

aws apigateway put-integration-response \
    --profile $PROFILE \
    --region $REGION \
    --rest-api-id $API_ID \
    --resource-id $SEARCH_RESOURCE_ID \
    --http-method OPTIONS \
    --status-code 200 \
    --response-parameters '{"method.response.header.Access-Control-Allow-Headers":"'\''Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'\''","method.response.header.Access-Control-Allow-Methods":"'\''GET,POST,PUT,DELETE,OPTIONS'\''","method.response.header.Access-Control-Allow-Origin":"'\''*'\''"}' \
    --response-templates '{"application/json": ""}'

# Dar permisos a API Gateway para invocar Lambda
aws lambda add-permission \
    --profile $PROFILE \
    --region $REGION \
    --function-name $FUNCTION_NAME \
    --statement-id apigateway-invoke-books \
    --action lambda:InvokeFunction \
    --principal apigateway.amazonaws.com \
    --source-arn "arn:aws:execute-api:$REGION:$ACCOUNT_ID:$API_ID/*/*"

# Desplegar API
aws apigateway create-deployment \
    --profile $PROFILE \
    --region $REGION \
    --rest-api-id $API_ID \
    --stage-name dev

echo "✅ API Gateway desplegado"
echo "🌐 URL Base: https://$API_ID.execute-api.$REGION.amazonaws.com/dev"
echo "📚 Endpoint Books: https://$API_ID.execute-api.$REGION.amazonaws.com/dev/books"
echo "🔍 Endpoint Search: https://$API_ID.execute-api.$REGION.amazonaws.com/dev/search?q=test"
