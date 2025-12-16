# Serverless Library Management System (LMS)

[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![AWS SAM](https://img.shields.io/badge/AWS-SAM-orange.svg)](https://aws.amazon.com/serverless/sam/)
[![DynamoDB](https://img.shields.io/badge/AWS-DynamoDB-blue.svg)](https://aws.amazon.com/dynamodb/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

A cost-optimized serverless Library Management System built with AWS Lambda, DynamoDB, and S3, following Clean Architecture principles.

## 🏗️ Architecture

- **Frontend**: Static website hosted on S3
- **Backend**: AWS Lambda functions with API Gateway
- **Database**: DynamoDB with single-table design
- **Infrastructure**: AWS SAM/CloudFormation
- **Cost**: ~$0.50/month for 500 items, 1000 requests/week

## 🚀 Quick Start

### Prerequisites
- AWS CLI configured with `immersion` profile
- SAM CLI installed
- Python 3.11+

### Deploy to AWS
```bash
# Clone and setup
git clone <repository-url>
cd library-management-system

# Deploy to development
./scripts/deploy.sh dev

# Seed database
python local/scripts/csv_to_dynamodb.py

# Get API URL from stack outputs
aws cloudformation describe-stacks --profile immersion --stack-name lms-serverless --query 'Stacks[0].Outputs'
```

### Local Development
```bash
# Start local environment
docker-compose up -d

# API available at: http://localhost:3000
# Frontend at: http://localhost:8080
# DynamoDB Local: http://localhost:8000
```

## 📁 Project Structure

```
library-management-system/
├── src/                          # Source code
│   ├── domain/                   # Domain layer (Clean Architecture)
│   │   ├── entities/            # Domain entities
│   │   └── repositories/        # Repository interfaces
│   ├── infrastructure/          # Infrastructure layer
│   │   └── dynamodb/           # DynamoDB implementations
│   └── application/            # Application layer
│       ├── use_cases/          # Business logic services
│       └── lambda_handlers/    # Lambda function handlers
├── docs/                       # Documentation
├── scripts/                    # Deployment scripts
├── layers/                     # Lambda layers
├── local/                      # Local development tools
├── template.yaml              # SAM template
└── docker-compose.yml         # Local development environment
```

## 🎯 Features

### Core Functionality
- ✅ **Book Management**: CRUD operations for books and copies
- ✅ **Member Management**: Library patron registration and management
- ✅ **Loan System**: Book checkout and return workflow
- ✅ **Ultra-fast Search**: <50ms autocomplete with single GSI
- ✅ **Cost Optimized**: 96% cost reduction through smart design

### Technical Features
- ✅ **Clean Architecture**: Domain-driven design with clear layer separation
- ✅ **Single Table Design**: DynamoDB optimization for cost and performance
- ✅ **Serverless**: Pay-per-use with automatic scaling
- ✅ **CORS Enabled**: Ready for frontend integration
- ✅ **Type Safety**: Pydantic models for validation

## 🔧 API Endpoints

### Search & Autocomplete
```bash
GET /search?q=book&type=book&limit=10
GET /autocomplete?q=har&type=book
```

### Books
```bash
GET /books                    # List books
GET /books/{book_id}         # Get book details
POST /books                  # Create book
```

### Members
```bash
GET /members                 # List members
GET /members/{member_id}     # Get member details
POST /members               # Create member
```

### Loans
```bash
GET /loans                   # List loans
POST /loans                  # Create loan
PUT /loans/{loan_id}/return  # Return book
```

## 💾 Database Design

### DynamoDB Single Table
- **Primary Key**: `pk` (partition key), `sk` (sort key)
- **GSI1**: `gsi1pk`, `gsi1sk` for search operations
- **Cost**: ~$0.001/month for 500 items

### Entity Patterns
```
Book:     pk=BOOK#{id}     sk=METADATA
Copy:     pk=BOOK#{id}     sk=COPY#{copy_id}
Member:   pk=MEMBER#{id}   sk=METADATA
Loan:     pk=LOAN#{id}     sk=METADATA
Search:   gsi1pk=SEARCH#{type}  gsi1sk={searchable_text}
```

## 🚀 Deployment

### Development Environment
```bash
./scripts/deploy.sh dev
```

### Production Environment
```bash
./scripts/deploy.sh prod
```

### Destroy Stack
```bash
./scripts/destroy.sh dev
```

See [DEPLOYMENT.md](docs/DEPLOYMENT.md) for detailed instructions.

## 🧪 Testing

### Local Testing
```bash
# Start local environment
docker-compose up -d

# Test API endpoints
curl http://localhost:3000/search?q=book
```

### Unit Tests
```bash
# Install dev dependencies
pip install pytest moto

# Run tests
pytest tests/
```

## 📊 Cost Analysis

### Monthly Costs (500 items, 1000 requests/week)
- **DynamoDB**: ~$0.001 (pay-per-request)
- **Lambda**: ~$0.20 (1M free requests/month)
- **API Gateway**: ~$0.25 (1M free requests/month)
- **S3**: ~$0.05 (static hosting)
- **Total**: ~$0.50/month

### Cost Optimizations Applied
- Single GSI instead of multiple indexes (96% reduction)
- Batch operations for data loading
- Shortened attribute names
- Pay-per-request billing
- Minimal Lambda memory allocation

## 🔄 Data Migration

### From PostgreSQL
The system includes migration tools from the original PostgreSQL schema:

```bash
# Convert CSV data to DynamoDB format
python local/scripts/csv_to_dynamodb.py

# Batch upload to DynamoDB
python local/scripts/batch_upload.py
```

## 📚 Documentation

- [Deployment Guide](docs/DEPLOYMENT.md)
- [Architecture Overview](docs/architecture/)
- [API Documentation](docs/api/)
- [Database Schema](docs/database/)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit changes: `git commit -m 'Add your feature'`
4. Push to branch: `git push origin feature/your-feature`
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🎯 Roadmap

- [ ] Frontend implementation with Tabler UI
- [ ] Employee management system
- [ ] Fine calculation system
- [ ] Reservation system
- [ ] Reporting dashboard
- [ ] Multi-language support (EN/ES)
- [ ] Mobile app integration
- [ ] Advanced search filters
- [ ] Email notifications
- [ ] Audit logging