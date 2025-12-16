#!/bin/bash

# Local Development Setup Script
# Usage: ./scripts/local-dev.sh [start|stop|restart]

set -e

ACTION=${1:-start}

case $ACTION in
    start)
        echo "🚀 Starting local development environment..."
        
        # Check prerequisites
        echo "🔍 Checking prerequisites..."
        
        if ! command -v aws &> /dev/null; then
            echo "❌ AWS CLI not found. Please install AWS CLI first."
            echo "   https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html"
            exit 1
        fi
        
        if ! command -v sam &> /dev/null; then
            echo "❌ SAM CLI not found. Please install SAM CLI first."
            echo "   https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html"
            exit 1
        fi
        
        echo "✅ AWS CLI and SAM CLI found"
        
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
                'IndexName=GSI1,KeySchema=[{AttributeName=gsi1pk,KeyType=HASH},{AttributeName=gsi1sk,KeyType=RANGE}],Projection={ProjectionType=ALL}' \
            --billing-mode PAY_PER_REQUEST \
            --endpoint-url http://localhost:8000 \
            --region us-east-1 2>/dev/null || echo "✅ Table already exists or created"
        
        # Build and start SAM application
        echo "🔨 Building SAM application..."
        sam build
        
        echo "🌐 Starting SAM Local API..."
        echo "API will be available at: http://localhost:3000"
        echo "DynamoDB Local: http://localhost:8000"
        echo "Frontend: http://localhost:8080"
        echo ""
        echo "Press Ctrl+C to stop"
        
        # Start frontend
        docker-compose up -d frontend
        
        # Set environment variables
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