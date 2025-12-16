#!/bin/bash
set -e

PROFILE="immersion"
REGION="us-east-1"
ACCOUNT_ID=$(aws sts get-caller-identity --profile $PROFILE --region $REGION --query Account --output text)
BUCKET_NAME="lms-static-$ACCOUNT_ID-$REGION"

echo "📤 Paso 6: Subiendo frontend a S3..."

# Verificar configuración de website (siempre)
if ! aws s3api get-bucket-website --profile $PROFILE --bucket $BUCKET_NAME 2>/dev/null; then
    echo "⚠️  Bucket sin configuración de website, configurando..."
    
    # Desbloquear acceso público
    aws s3api put-public-access-block \
        --profile $PROFILE \
        --region $REGION \
        --bucket $BUCKET_NAME \
        --public-access-block-configuration "BlockPublicAcls=false,IgnorePublicAcls=false,BlockPublicPolicy=false,RestrictPublicBuckets=false"
    
    # Configurar website
    aws s3 website s3://$BUCKET_NAME \
        --profile $PROFILE \
        --region $REGION \
        --index-document index.html \
        --error-document error.html
    
    # Aplicar política pública
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
    
    rm -f /tmp/bucket-policy.json
    echo "✅ Configuración de website aplicada"
fi

# Verificar si ya hay archivos en el bucket
FILE_COUNT=$(aws s3 ls s3://$BUCKET_NAME --profile $PROFILE --region $REGION 2>/dev/null | wc -l)
if [ "$FILE_COUNT" -gt "0" ]; then
    echo "⏭️  El bucket ya tiene $FILE_COUNT archivos, saltando subida..."
    exit 0
fi

echo "Bucket vacío, subiendo archivos..."

# Subir archivos
aws s3 sync frontend/src/ s3://$BUCKET_NAME/ --profile $PROFILE --region $REGION --delete

echo "✅ Frontend subido"
echo "🌐 URL: http://$BUCKET_NAME.s3-website-$REGION.amazonaws.com"
echo ""
echo "🧪 Verificando frontend..."
echo "Archivos en S3:"
aws s3 ls s3://$BUCKET_NAME --profile $PROFILE --region $REGION
echo ""
echo "Probando acceso al sitio:"
curl -s -o /dev/null -w "Status: %{http_code}\n" "http://$BUCKET_NAME.s3-website-$REGION.amazonaws.com"
echo "✅ Verificación exitosa"
