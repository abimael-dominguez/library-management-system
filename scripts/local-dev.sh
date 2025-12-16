#!/bin/bash

# Local Development Setup Script
# Usage: ./scripts/local-dev.sh [start|stop|restart]

set -e

ACTION=${1:-start}

case $ACTION in
    start)
        echo "🚀 Starting local development environment..."
        
        # Start DynamoDB Local
        echo "📦 Starting DynamoDB Local..."
        docker-compose up -d dynamodb-local
        
        # Wait for DynamoDB to be ready
        echo "⏳ Waiting for DynamoDB Local to be ready..."
        sleep 5
        
        # Create local table
        echo "🗄️  Creating local DynamoDB table..."
        aws dynamodb create-table \
            --table-name lms-local \
            --attribute-definitions \
                AttributeName=pk,AttributeType=S \
                AttributeName=sk,AttributeType=S \
                AttributeName=gsi1pk,AttributeType=S \
                AttributeName=gsi1sk,AttributeType=S \
            --key-schema \
                AttributeName=pk,KeyType=HASH \
                AttributeName=sk,KeyType=RANGE \
            --global-secondary-indexes \
                IndexName=GSI1,KeySchema=[{AttributeName=gsi1pk,KeyType=HASH},{AttributeName=gsi1sk,KeyType=RANGE}],Projection={ProjectionType=ALL},BillingMode=PAY_PER_REQUEST \
            --billing-mode PAY_PER_REQUEST \
            --endpoint-url http://localhost:8000 \
            --region us-east-1 || echo "Table might already exist"
        
        # Build SAM application
        echo "🔨 Building SAM application..."
        sam build
        
        # Start SAM Local API
        echo "🌐 Starting SAM Local API..."
        echo "API will be available at: http://localhost:3000"
        echo "DynamoDB Local: http://localhost:8000"
        echo ""
        echo "Press Ctrl+C to stop"
        
        # Set environment variables for local development
        export DYNAMODB_TABLE=lms-local
        export DYNAMODB_ENDPOINT=http://localhost:8000
        export AWS_ACCESS_KEY_ID=dummy
        export AWS_SECRET_ACCESS_KEY=dummy
        export AWS_DEFAULT_REGION=us-east-1
        
        sam local start-api \
            --host 0.0.0.0 \
            --port 3000 \
            --docker-network lms_network \
            --parameter-overrides "Environment=local" \
            --env-vars local/env.json
        ;;
        
    stop)
        echo "🛑 Stopping local development environment..."
        docker-compose down
        echo "✅ Local environment stopped"
        ;;
        
    restart)
        echo "🔄 Restarting local development environment..."
        $0 stop
        sleep 2
        $0 start
        ;;
        
    *)
        echo "Usage: $0 [start|stop|restart]"
        exit 1
        ;;
esac