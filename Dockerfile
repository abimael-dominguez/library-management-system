FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ src/
COPY alembic/ alembic/
COPY alembic.ini .
COPY tests/ tests/
COPY scripts/ scripts/
COPY pytest.ini .
COPY frontend/ frontend/

ENV PYTHONPATH=/app:/app/src

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
