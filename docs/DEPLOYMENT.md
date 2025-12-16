# LMS Deployment Guide

## Prerequisites

1. **AWS CLI** configured with `immersion` profile
2. **SAM CLI** installed
3. **Python 3.11+** for local development
4. **Git** for version control

## Quick Start

### Deploy to Development
```bash
./scripts/deploy.sh dev
```

### Deploy to Production
```bash
./scripts/deploy.sh prod
```

### Destroy Stack
```bash
./scripts/destroy.sh dev  # or prod
```

## Manual Deployment Steps

### 1. Build Lambda Layer
```bash
cd layers/dependencies
pip install -r requirements.txt -t python/
cd ../..
```

### 2. Build SAM Application
```bash
sam build --profile immersion
```

### 3. Deploy Stack
```bash
# Development
sam deploy --profile immersion --config-env default

# Production
sam deploy --profile immersion --config-env prod
```

### 4. Get Stack Outputs
```bash
aws cloudformation describe-stacks \
    --profile immersion \
    --stack-name lms-serverless \
    --query 'Stacks[0].Outputs[*].[OutputKey,OutputValue]' \
    --output table
```

## Stack Resources

### DynamoDB
- **Table**: `lms-{environment}`
- **Billing**: Pay-per-request
- **GSI**: Single GSI for all search operations
- **Estimated Cost**: ~$0.001/month for 500 items

### Lambda Functions
- **Search**: Autocomplete and search operations
- **Loans**: Loan/return operations
- **Books**: Book CRUD operations
- **Members**: Member CRUD operations
- **Runtime**: Python 3.11
- **Memory**: 256MB
- **Timeout**: 30 seconds

### API Gateway
- **Type**: REST API
- **CORS**: Enabled for all origins
- **Stage**: Environment-based (dev/prod)

### S3 Bucket
- **Name**: `lms-static-data-{environment}`
- **Purpose**: Static website hosting
- **Public Access**: Read-only

## Environment Configuration

### Development (dev)
- Stack: `lms-serverless`
- DynamoDB: `lms-dev`
- S3: `lms-static-data-dev`

### Production (prod)
- Stack: `lms-serverless-prod`
- DynamoDB: `lms-prod`
- S3: `lms-static-data-prod`

## Post-Deployment Steps

### 1. Seed Database
```bash
# Update table name in script
python local/scripts/csv_to_dynamodb.py
```

### 2. Upload Frontend
```bash
# Get bucket name from stack outputs
aws s3 sync frontend/ s3://lms-static-data-dev/ --profile immersion
```

### 3. Test API
```bash
# Get API URL from stack outputs
curl https://your-api-id.execute-api.us-east-1.amazonaws.com/dev/search?q=book
```

## Rollback Procedures

### Rollback to Previous Version
```bash
# List stack events to find previous version
aws cloudformation describe-stack-events \
    --profile immersion \
    --stack-name lms-serverless

# Rollback using CloudFormation
aws cloudformation cancel-update-stack \
    --profile immersion \
    --stack-name lms-serverless
```

### Complete Stack Deletion
```bash
./scripts/destroy.sh dev
```

## Troubleshooting

### Common Issues

1. **SAM build fails**
   - Check Python version (3.11+ required)
   - Verify requirements.txt syntax

2. **Deployment fails**
   - Check AWS credentials: `aws sts get-caller-identity --profile immersion`
   - Verify region is us-east-1

3. **Lambda function errors**
   - Check CloudWatch logs
   - Verify environment variables

4. **API Gateway CORS issues**
   - CORS is pre-configured in template
   - Check browser developer tools

### Monitoring

- **CloudWatch Logs**: `/aws/lambda/lms-{function}-{env}`
- **DynamoDB Metrics**: CloudWatch DynamoDB dashboard
- **API Gateway Metrics**: CloudWatch API Gateway dashboard

## Cost Optimization

- **DynamoDB**: Pay-per-request billing
- **Lambda**: Pay-per-invocation
- **API Gateway**: Pay-per-request
- **S3**: Pay-per-storage and requests

**Estimated monthly cost for 500 items, 1000 requests/week**: ~$0.50