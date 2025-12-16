# Guía de Despliegue - Library Management System

## Requisitos Previos
- AWS CLI configurado con perfil `immersion`
- Python 3.11+
- Docker y Docker Compose
- Permisos en AWS para crear: DynamoDB, S3, Lambda, API Gateway, IAM

## Despliegue Completo (Opción 1)

```bash
# Ejecutar todos los pasos automáticamente
./scripts/deploy-all.sh
```

El script pausará para que actualices el `API_BASE_URL` en `frontend/src/app.js`.

## Despliegue Paso a Paso (Opción 2)

### Paso 1: Crear DynamoDB
```bash
./scripts/deploy-step1-dynamodb.sh
```
Crea tabla `lms-table-dev` con GSI1 para búsqueda.

### Paso 2: Crear S3 Bucket
```bash
./scripts/deploy-step2-s3.sh
```
Crea bucket público para hosting estático.

### Paso 3: Crear Lambda Function
```bash
./scripts/deploy-step3-lambda.sh
```
Crea función Lambda con rol IAM y permisos DynamoDB.

### Paso 4: Crear API Gateway
```bash
./scripts/deploy-step4-api.sh
```
Crea API REST con endpoints `/books` y `/search` con CORS configurado.

### Paso 5: Actualizar Frontend
```bash
# Obtener API URL
API_ID=$(aws apigateway get-rest-apis --profile immersion --query 'items[?name==`lms-api-dev`].id' --output text)
echo "https://$API_ID.execute-api.us-east-1.amazonaws.com/dev"

# Actualizar frontend/src/app.js con la URL
# Cambiar: const API_BASE_URL = 'https://XXXXX.execute-api.us-east-1.amazonaws.com/dev';
```

### Paso 6: Subir Frontend
```bash
./scripts/deploy-step5-frontend.sh
```

### Paso 7: Cargar Datos
```bash
# Iniciar contenedor Docker
docker-compose up -d

# Cargar datos a DynamoDB
docker exec -it lms-seed python /app/seed_dynamodb.py
```

## Verificación

```bash
# Verificar DynamoDB
aws dynamodb describe-table --profile immersion --table-name lms-table-dev

# Verificar Lambda
aws lambda get-function --profile immersion --function-name lms-books-dev

# Verificar API
curl "https://$API_ID.execute-api.us-east-1.amazonaws.com/dev/books?limit=5"

# Verificar Frontend
ACCOUNT_ID=$(aws sts get-caller-identity --profile immersion --query Account --output text)
echo "http://lms-static-$ACCOUNT_ID-us-east-1.s3-website-us-east-1.amazonaws.com"
```

## Limpieza

```bash
# Eliminar todos los recursos
./scripts/cleanup-aws.sh
```

## Recursos Creados

1. **DynamoDB**: `lms-table-dev`
   - Tabla con single-table design
   - GSI1 para búsqueda optimizada

2. **S3**: `lms-static-{ACCOUNT_ID}-us-east-1`
   - Bucket público para hosting
   - Configurado como sitio web estático

3. **Lambda**: `lms-books-dev`
   - Runtime: Python 3.11
   - Handler: `books_handler_cors.lambda_handler`
   - Variables: `DYNAMODB_TABLE`, `ENVIRONMENT`

4. **API Gateway**: `lms-api-dev`
   - Endpoints: `/books`, `/search`
   - CORS habilitado
   - Stage: `dev`

5. **IAM Role**: `lms-lambda-role`
   - Políticas: AWSLambdaBasicExecutionRole, AmazonDynamoDBFullAccess

## Troubleshooting

### Error: "Table already exists"
```bash
aws dynamodb delete-table --profile immersion --table-name lms-table-dev
```

### Error: "Role already exists"
El script continúa si el rol ya existe.

### Error: CORS en el navegador
- Verificar que OPTIONS esté configurado en API Gateway
- Hacer hard refresh: Ctrl+Shift+R
- Verificar que el API_BASE_URL sea correcto

### Lambda no encuentra datos
```bash
# Verificar variable de entorno
aws lambda get-function-configuration --profile immersion --function-name lms-books-dev

# Verificar datos en DynamoDB
aws dynamodb scan --profile immersion --table-name lms-table-dev --limit 5
```

## Costos Estimados

- **DynamoDB**: ~$0.001/mes (500 items, pay-per-request)
- **Lambda**: ~$0.20/mes (1M requests gratis)
- **API Gateway**: ~$0.25/mes (1M requests gratis)
- **S3**: ~$0.05/mes (hosting estático)
- **Total**: ~$0.50/mes
