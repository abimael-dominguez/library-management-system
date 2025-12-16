#!/bin/bash
set -e

PROFILE="immersion"
REGION="us-east-1"
ACCOUNT_ID=$(aws sts get-caller-identity --profile $PROFILE --region $REGION --query Account --output text)
BUCKET_NAME="lms-static-$ACCOUNT_ID-$REGION"

echo "🪣 Paso 2: Creando S3 bucket..."

# Crear bucket
aws s3 mb s3://$BUCKET_NAME --profile $PROFILE --region $REGION

# Configurar como sitio web
aws s3 website s3://$BUCKET_NAME \
    --profile $PROFILE \
    --index-document index.html \
    --error-document error.html

# Desbloquear acceso público PRIMERO
aws s3api put-public-access-block \
    --profile $PROFILE \
    --bucket $BUCKET_NAME \
    --public-access-block-configuration "BlockPublicAcls=false,IgnorePublicAcls=false,BlockPublicPolicy=false,RestrictPublicBuckets=false"

# Esperar un momento
sleep 3

# Política pública para lectura
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
    --bucket $BUCKET_NAME \
    --policy file:///tmp/bucket-policy.json

echo "✅ S3 bucket creado: $BUCKET_NAME"
echo "🌐 URL: http://$BUCKET_NAME.s3-website-$REGION.amazonaws.com"
echo "📤 Subir archivos: aws s3 sync frontend/src/ s3://$BUCKET_NAME/ --profile $PROFILE"