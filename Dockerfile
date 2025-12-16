FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ src/
COPY tests/ tests/
COPY pytest.ini .

# Set Python path
ENV PYTHONPATH=/app

# Default command to run tests
CMD ["pytest", "-v", "--cov=src", "--cov-report=term-missing", "--cov-report=html"]