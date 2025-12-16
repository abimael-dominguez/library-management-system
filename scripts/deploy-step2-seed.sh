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
echo "🔍 Verificar: aws dynamodb scan --profile immersion --table-name lms-table-dev --select COUNT"
