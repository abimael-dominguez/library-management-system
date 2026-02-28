#!/bin/bash
set -e

PROFILE="immersion"
REGION="us-east-1"
TABLE_NAME="lms-table-dev"

wait_for_table_active() {
    local profile="$1"
    local region="$2"
    local table_name="$3"
    local max_attempts=60
    local attempt=1
    local status

    echo "⏳ Esperando a que la tabla $table_name esté ACTIVE..."
    while [ "$attempt" -le "$max_attempts" ]; do
        status=$(aws dynamodb describe-table \
            --profile "$profile" \
            --region "$region" \
            --table-name "$table_name" \
            --query 'Table.TableStatus' \
            --output text 2>/dev/null || echo "NOT_FOUND")

        if [ "$status" = "ACTIVE" ]; then
            echo "✅ Tabla $table_name en estado ACTIVE"
            return 0
        fi

        echo "   Intento $attempt/$max_attempts - estado actual: $status"
        sleep 5
        attempt=$((attempt + 1))
    done

    echo "❌ Timeout esperando que $table_name esté ACTIVE"
    return 1
}

echo "🗄️  Paso 1: Creando DynamoDB..."

# Verificar si la tabla ya existe
if aws dynamodb describe-table --profile $PROFILE --region $REGION --table-name $TABLE_NAME &>/dev/null; then
    echo "⏭️  Tabla $TABLE_NAME ya existe"
    wait_for_table_active "$PROFILE" "$REGION" "$TABLE_NAME"
    aws dynamodb describe-table --profile $PROFILE --region $REGION --table-name $TABLE_NAME --query 'Table.[TableName,TableStatus,ItemCount]' --output table
    exit 0
fi

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
    --billing-mode PAY_PER_REQUEST \
    --no-cli-pager > /dev/null

echo "✅ DynamoDB creado: $TABLE_NAME"
wait_for_table_active "$PROFILE" "$REGION" "$TABLE_NAME"
echo ""
echo "🧪 Verificando instalación..."
aws dynamodb describe-table --profile $PROFILE --region $REGION --table-name $TABLE_NAME --query 'Table.[TableName,TableStatus,ItemCount]' --output table
echo "✅ Verificación exitosa"
