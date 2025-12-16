# LMS Architecture Guide

## Clean Architecture + DDD Structure

### Layer Organization

#### Domain Layer (`src/domain/`)
- **entities/**: Core business entities (Book, Member, Loan, Employee)
- **value_objects/**: Immutable objects (ISBN, Email, Status)
- **aggregates/**: Business logic aggregates
- **repositories/**: Abstract repository interfaces
- **services/**: Domain services for business logic

#### Infrastructure Layer (`src/infrastructure/`)
- **dynamodb/**: DynamoDB repository implementations
- **aws_services/**: AWS SDK integrations
- **external_apis/**: External service adapters

#### Application Layer (`src/application/`)
- **use_cases/**: Application use cases (CreateLoan, ReturnBook)
- **dtos/**: Data Transfer Objects for API
- **validators/**: Pydantic validators
- **lambda_handlers/**: AWS Lambda function handlers
- **composition_root/**: Dependency injection setup

### Lambda Function Mapping
- Books Lambda: Book CRUD operations
- Members Lambda: Member management
- Loans Lambda: Loan/return operations
- Search Lambda: Autocomplete functionality
- Auth Lambda: Authentication (if needed)

### Development Workflow
1. Define domain entities and value objects
2. Create repository interfaces in domain
3. Implement repositories in infrastructure layer
4. Create use cases in application layer
5. Implement Lambda handlers
6. Deploy with CloudFormation/SAM
