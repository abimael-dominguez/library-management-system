#!/usr/bin/env python3
"""
Project Scaffolder for Serverless LMS
Creates Clean Architecture/DDD structure for AWS Lambda-based Library Management System
"""

import os
from pathlib import Path

def create_directory_structure():
    """Create the Clean Architecture/DDD directory structure"""
    
    base_dirs = {
        # Domain Layer - Core business logic
        "src/domain": [
            "entities",
            "value_objects", 
            "aggregates",
            "repositories",
            "services",
            "__init__.py"
        ],
        
        # Driven Layer - Infrastructure adapters
        "src/driven": [
            "dynamodb",
            "aws_services",
            "external_apis",
            "__init__.py"
        ],
        
        # Design Layer - Application services, use cases, API handlers
        "src/design": [
            "use_cases",
            "dtos",
            "validators",
            "lambda_handlers",
            "composition_root",
            "__init__.py"
        ],
        
        # Shared utilities
        "src/shared": [
            "utils",
            "constants",
            "exceptions",
            "__init__.py"
        ],
        
        # Infrastructure as Code
        "infrastructure": [
            "cloudformation",
            "sam"
        ],
        
        # Frontend
        "frontend": [
            "src",
            "assets",
            "i18n"
        ],
        
        # Local development
        "local": [
            "docker",
            "scripts",
            "data"
        ],
        
        # Tests
        "tests": [
            "unit",
            "integration",
            "fixtures"
        ],
        
        # Documentation
        "docs": [
            "api",
            "architecture", 
            "deployment"
        ]
    }
    
    # Create directories
    for base_dir, subdirs in base_dirs.items():
        base_path = Path(base_dir)
        base_path.mkdir(parents=True, exist_ok=True)
        
        for subdir in subdirs:
            if subdir.endswith('.py'):
                # Create __init__.py files
                (base_path / subdir).touch()
            else:
                # Create subdirectory
                (base_path / subdir).mkdir(exist_ok=True)
                (base_path / subdir / "__init__.py").touch()
    
    print("✅ Directory structure created successfully!")

def create_initial_files():
    """Create initial configuration and documentation files"""
    
    files_to_create = {
        "requirements.txt": """# Core dependencies
pydantic>=2.0.0
boto3>=1.34.0
aws-lambda-powertools>=2.0.0

# Development dependencies
pytest>=7.0.0
pytest-mock>=3.0.0
black>=23.0.0
mypy>=1.0.0
""",
        
        "src/__init__.py": "",
        
        "src/shared/constants/__init__.py": """# Shared constants for the LMS application
AWS_REGION = "us-east-1"
DYNAMODB_TABLE_PREFIX = "lms"
S3_BUCKET_NAME = "lms-static-data"
""",
        
        "src/shared/exceptions/__init__.py": """# Custom exceptions for the LMS application

class LMSException(Exception):
    \"\"\"Base exception for LMS application\"\"\"
    pass

class BookNotFoundError(LMSException):
    \"\"\"Raised when a book is not found\"\"\"
    pass

class MemberNotFoundError(LMSException):
    \"\"\"Raised when a member is not found\"\"\"
    pass

class LoanNotFoundError(LMSException):
    \"\"\"Raised when a loan is not found\"\"\"
    pass

class ValidationError(LMSException):
    \"\"\"Raised when validation fails\"\"\"
    pass
""",
        
        "README_ARCHITECTURE.md": """# LMS Architecture Guide

## Clean Architecture + DDD Structure

### Layer Organization

#### Domain Layer (`src/domain/`)
- **entities/**: Core business entities (Book, Member, Loan, Employee)
- **value_objects/**: Immutable objects (ISBN, Email, Status)
- **aggregates/**: Business logic aggregates
- **repositories/**: Abstract repository interfaces
- **services/**: Domain services for business logic

#### Driven Layer (`src/driven/`)
- **dynamodb/**: DynamoDB repository implementations
- **aws_services/**: AWS SDK integrations
- **external_apis/**: External service adapters

#### Design Layer (`src/design/`)
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
3. Implement repositories in driven layer
4. Create use cases in design layer
5. Implement Lambda handlers
6. Deploy with CloudFormation/SAM
""",
        
        "local/docker/Dockerfile": """FROM ubuntu:22.04

# Install Python and dependencies
RUN apt-get update && apt-get install -y \\
    python3 \\
    python3-pip \\
    python3-venv \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Install AWS CLI and SAM CLI
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" \\
    && unzip awscliv2.zip \\
    && ./aws/install \\
    && rm -rf aws awscliv2.zip

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# Copy application code
COPY . .

# Default command
CMD ["python3", "-m", "pytest", "tests/"]
""",
        
        ".env.example": """# AWS Configuration
AWS_PROFILE=immersion
AWS_REGION=us-east-1

# DynamoDB Configuration
DYNAMODB_TABLE_PREFIX=lms
DYNAMODB_ENDPOINT_URL=http://localhost:8000

# S3 Configuration
S3_BUCKET_NAME=lms-static-data

# Local Development
LOCAL_DEVELOPMENT=true
LOG_LEVEL=DEBUG
"""
    }
    
    for file_path, content in files_to_create.items():
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
    
    print("✅ Initial files created successfully!")

def main():
    """Main scaffolder function"""
    print("🚀 Creating Serverless LMS Project Structure...")
    print("📁 Setting up Clean Architecture/DDD layers...")
    
    create_directory_structure()
    create_initial_files()
    
    print("\n✨ Project scaffolding completed!")
    print("\n📋 Next steps:")
    print("1. Review the created structure")
    print("2. Install dependencies: pip install -r requirements.txt")
    print("3. Copy .env.example to .env and configure")
    print("4. Start implementing domain entities")
    print("\n📖 See README_ARCHITECTURE.md for detailed guidance")

if __name__ == "__main__":
    main()