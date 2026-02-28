#!/bin/bash
set -e

PROFILE="immersion"
REGION="us-east-1"
VENV_DIR=".transfer_data_env"
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

echo "📊 Paso 2: Cargando datos a DynamoDB..."

# Verificar si ya hay datos
ITEM_COUNT=$(aws dynamodb scan --profile $PROFILE --region $REGION --table-name $TABLE_NAME --select COUNT --query 'Count' --output text 2>/dev/null || echo "0")
if [ "$ITEM_COUNT" -gt "0" ]; then
    echo "⏭️  La tabla ya tiene $ITEM_COUNT items, saltando..."
    exit 0
fi

# Verificar que la tabla existe
if ! aws dynamodb describe-table --profile $PROFILE --region $REGION --table-name $TABLE_NAME &>/dev/null; then
    echo "❌ Error: La tabla $TABLE_NAME no existe"
    exit 1
fi

# Asegurar que la tabla esté lista para escrituras
wait_for_table_active "$PROFILE" "$REGION" "$TABLE_NAME"

# Crear venv temporal
echo "🐍 Creando virtual environment temporal..."
python3 -m venv $VENV_DIR
echo "📦 Instalando dependencias..."
$VENV_DIR/bin/pip install -q --upgrade pip
$VENV_DIR/bin/pip install -q boto3

# Ejecutar seed
echo "📥 Cargando datos..."
if [ -f "scripts/seed-data.py" ]; then
    $VENV_DIR/bin/python scripts/seed-data.py
else
    rm -rf $VENV_DIR
    echo "❌ Error: scripts/seed-data.py no encontrado"
    exit 1
fi

# Limpiar venv temporal
echo "🧹 Limpiando environment temporal..."
rm -rf $VENV_DIR

echo "✅ Datos cargados exitosamente"
echo ""
echo "🧪 Verificando datos..."
echo "Conteo de items por tipo:"
BOOK_COUNT=$(aws dynamodb scan --profile $PROFILE --region $REGION --table-name $TABLE_NAME --filter-expression "entity_type = :t" --expression-attribute-values '{":t":{"S":"book"}}' --select COUNT --query 'Count' --output text)
MEMBER_COUNT=$(aws dynamodb scan --profile $PROFILE --region $REGION --table-name $TABLE_NAME --filter-expression "entity_type = :t" --expression-attribute-values '{":t":{"S":"member"}}' --select COUNT --query 'Count' --output text)
echo "  - Libros: $BOOK_COUNT"
echo "  - Miembros: $MEMBER_COUNT"
echo ""
echo "Primeros 5 libros:"
aws dynamodb scan --profile $PROFILE --region $REGION --table-name $TABLE_NAME --filter-expression "entity_type = :t" --expression-attribute-values '{":t":{"S":"book"}}' --limit 5 --query 'Items[*].[title.S,author.S]' --output table
echo "✅ Verificación exitosa"
