#!/bin/bash
set -e

echo "📊 Paso 6: Cargando datos a DynamoDB..."

# Verificar si Docker está corriendo
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker no está corriendo"
    exit 1
fi

# Iniciar contenedor si no está corriendo
if ! docker ps | grep -q lms-seed; then
    echo "🐳 Iniciando contenedor Docker..."
    docker-compose up -d
    sleep 3
fi

# Ejecutar seed
echo "📥 Cargando datos..."
docker exec -it lms-seed python /app/seed_dynamodb.py

echo "✅ Datos cargados exitosamente"
echo ""
echo "🧪 Verificando datos..."
echo "Conteo de items por tipo:"
aws dynamodb scan --profile immersion --table-name lms-table-dev --filter-expression "entity_type = :t" --expression-attribute-values '{":t":{"S":"book"}}' --select COUNT --query 'Count' --output text | xargs -I {} echo "  - Libros: {}"
aws dynamodb scan --profile immersion --table-name lms-table-dev --filter-expression "entity_type = :t" --expression-attribute-values '{":t":{"S":"member"}}' --select COUNT --query 'Count' --output text | xargs -I {} echo "  - Miembros: {}"
echo ""
echo "Primeros 5 libros:"
aws dynamodb scan --profile immersion --table-name lms-table-dev --filter-expression "entity_type = :t" --expression-attribute-values '{":t":{"S":"book"}}' --limit 5 --query 'Items[*].[title.S,author.S]' --output table
echo "✅ Verificación exitosa"
