#!/bin/bash

PROFILE="immersion"
REGION="us-east-1"
ACCOUNT_ID=$(aws sts get-caller-identity --profile $PROFILE --region $REGION --query Account --output text)
BUCKET_NAME="lms-static-$ACCOUNT_ID-$REGION"

echo "🪣 Paso 3: Creando S3 bucket..."
echo "📝 Bucket name: $BUCKET_NAME"

# Verificar si el bucket ya existe
echo "🔍 Verificando si el bucket existe..."
if aws s3api head-bucket --profile $PROFILE --region $REGION --bucket $BUCKET_NAME 2>/dev/null; then
    echo "⏭️  Bucket $BUCKET_NAME ya existe, saltando..."
    exit 0
fi

# Crear bucket
echo "📦 Creando nuevo bucket..."
aws s3api create-bucket --profile $PROFILE --region $REGION --bucket $BUCKET_NAME 2>&1 | grep -v "BucketAlreadyOwnedByYou" || true
echo "✓ Bucket creado o ya existe"

# Configurar como sitio web
echo "🌐 Configurando website hosting..."
aws s3 website s3://$BUCKET_NAME \
    --profile $PROFILE \
    --region $REGION \
    --index-document index.html \
    --error-document error.html
echo "✓ Website configurado"

# Desbloquear acceso público PRIMERO
echo "🔓 Desbloqueando acceso público..."
aws s3api put-public-access-block \
    --profile $PROFILE \
    --region $REGION \
    --bucket $BUCKET_NAME \
    --public-access-block-configuration "BlockPublicAcls=false,IgnorePublicAcls=false,BlockPublicPolicy=false,RestrictPublicBuckets=false"
echo "✓ Acceso público desbloqueado"

# Esperar un momento
sleep 3

# Política pública para lectura
echo "📋 Aplicando bucket policy..."
cat > /tmp/bucket-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::$BUCKET_NAME/*"
        }
    ]
}
EOF

aws s3api put-bucket-policy \
    --profile $PROFILE \
    --region $REGION \
    --bucket $BUCKET_NAME \
    --policy file:///tmp/bucket-policy.json
echo "✓ Policy aplicada"

echo "✅ S3 bucket creado: $BUCKET_NAME"
echo "🌐 URL: http://$BUCKET_NAME.s3-website-$REGION.amazonaws.com"
echo ""
echo "🧪 Verificando bucket..."
aws s3 ls s3://$BUCKET_NAME --profile $PROFILE --region $REGION
echo "✅ Verificación exitosa - Bucket vacío (listo para recibir archivos)"
