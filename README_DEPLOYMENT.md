# Library Management System - Deployment Guide

## 🧪 Testing (Required Before Deployment)

### Prerequisites
- Docker and Docker Compose installed
- Git repository cloned locally

### Run Tests
```bash
# Run all tests with coverage
./scripts/test.sh

# Or manually with Docker Compose
docker-compose run --rm test
```

**✅ All tests must pass before proceeding to deployment!**

Current test coverage: **69%** (34 tests passing)

## 🚀 AWS Deployment

### Prerequisites
- AWS CLI configured with `immersion` profile
- SAM CLI installed
- Python 3.11+

### 1. Deploy Infrastructure
```bash
# Deploy to development environment
./scripts/deploy.sh dev

# Deploy to production environment  
./scripts/deploy.sh prod
```

### 2. Seed Database
After successful deployment, seed the database with initial data:

```bash
# Update table name in scripts/seed-data.py if needed
python scripts/seed-data.py
```

### 3. Upload Frontend
```bash
# Get S3 bucket name from stack outputs
aws cloudformation describe-stacks \
    --profile immersion \
    --stack-name lms-serverless-dev \
    --query 'Stacks[0].Outputs[?OutputKey==`S3Bucket`].OutputValue' \
    --output text

# Upload frontend files
aws s3 sync frontend/src/ s3://YOUR-BUCKET-NAME/ --profile immersion

# Update API URL in frontend/src/app.js
# Replace API_BASE_URL with your actual API Gateway URL
```

### 4. Get Deployment URLs
```bash
# Get all stack outputs
aws cloudformation describe-stacks \
    --profile immersion \
    --stack-name lms-serverless-dev \
    --query 'Stacks[0].Outputs' \
    --output table
```

## 🔧 Configuration

### Environment Variables
The Lambda functions use these environment variables:
- `DYNAMODB_TABLE`: DynamoDB table name (auto-configured)
- `ENVIRONMENT`: Deployment environment (dev/prod)

### DynamoDB Table Structure
Single table design with the following patterns:
- **Books**: `pk=BOOK#{id}`, `sk=METADATA`
- **Book Copies**: `pk=BOOK#{id}`, `sk=COPY#{copy_id}`
- **Members**: `pk=MEMBER#{id}`, `sk=METADATA`
- **Loans**: `pk=LOAN#{id}`, `sk=METADATA`
- **Search Index**: `gsi1pk=SEARCH#{type}`, `gsi1sk={searchable_text}`

## 📊 Cost Estimation

### Monthly Costs (500 items, 1000 requests/week)
- **DynamoDB**: ~$0.001 (pay-per-request)
- **Lambda**: ~$0.20 (1M free requests/month)
- **API Gateway**: ~$0.25 (1M free requests/month)
- **S3**: ~$0.05 (static hosting)
- **Total**: ~$0.50/month

## 🔄 Management Commands

### Update Stack
```bash
# Update with new changes
sam deploy --profile immersion

# Update specific environment
./scripts/deploy.sh dev
```

### Rollback
```bash
# Rollback via CloudFormation
aws cloudformation cancel-update-stack \
    --profile immersion \
    --stack-name lms-serverless-dev

# Or delete and redeploy
aws cloudformation delete-stack \
    --profile immersion \
    --stack-name lms-serverless-dev
```

### Delete Stack
```bash
# Delete everything
aws cloudformation delete-stack \
    --profile immersion \
    --stack-name lms-serverless-dev

# Clean up S3 bucket manually if needed
aws s3 rm s3://YOUR-BUCKET-NAME --recursive --profile immersion
```

## 🧪 Local Development

### Start Local Environment
```bash
# Start DynamoDB Local and API
docker-compose up -d

# API available at: http://localhost:3000
# DynamoDB Local: http://localhost:8000
```

### Test API Endpoints
```bash
# List books
curl http://localhost:3000/books

# Search books
curl "http://localhost:3000/search?q=python&limit=5"

# Create book
curl -X POST http://localhost:3000/books \
  -H "Content-Type: application/json" \
  -d '{"title":"Test Book","author":"Test Author"}'
```

## 🔍 Monitoring

### CloudWatch Logs
```bash
# View Lambda logs
aws logs describe-log-groups --profile immersion | grep lms

# Tail logs
sam logs --name BooksFunction --stack-name lms-serverless-dev --tail --profile immersion
```

### DynamoDB Metrics
- Monitor read/write capacity units
- Track throttling events
- Monitor GSI usage

## 🚨 Troubleshooting

### Common Issues

1. **Tests Failing**
   - Ensure all dependencies are installed
   - Check Docker is running
   - Review test output for specific errors

2. **Deployment Fails**
   - Verify AWS credentials and profile
   - Check SAM CLI version
   - Ensure unique S3 bucket names

3. **API Errors**
   - Check Lambda function logs
   - Verify DynamoDB permissions
   - Test with simplified requests

4. **Frontend Not Loading**
   - Verify S3 bucket policy
   - Check CORS configuration
   - Update API URL in app.js

### Debug Commands
```bash
# Validate SAM template
sam validate --profile immersion

# Build locally
sam build --profile immersion

# Test function locally
sam local invoke BooksFunction --event events/test-event.json --profile immersion
```

## 📚 API Documentation

### Endpoints

#### Books
- `GET /books` - List all books
- `POST /books` - Create new book
- `GET /books/{id}` - Get book details
- `GET /search?q={query}` - Search books
- `GET /autocomplete?q={query}&type=book` - Autocomplete

#### Loans
- `GET /loans` - List all loans
- `POST /loans` - Create new loan
- `GET /loans/{id}` - Get loan details
- `PUT /loans/{id}/return` - Return book

### Request/Response Examples

#### Create Book
```json
POST /books
{
  "title": "Python Programming",
  "author": "John Doe",
  "isbn": "978-0123456789",
  "pages": 300,
  "max_loan_weeks": 3,
  "total_copies": 2
}
```

#### Create Loan
```json
POST /loans
{
  "book_copy_id": "book-123-001",
  "member_id": "member-456",
  "employee_id": "employee-789"
}
```

## 🎯 Next Steps

After successful deployment:

1. **Test all API endpoints**
2. **Verify frontend functionality**
3. **Set up monitoring alerts**
4. **Configure backup policies**
5. **Document operational procedures**
6. **Train users on the system**

## 📞 Support

For issues or questions:
1. Check CloudWatch logs
2. Review this documentation
3. Test locally with Docker
4. Verify AWS permissions and quotas