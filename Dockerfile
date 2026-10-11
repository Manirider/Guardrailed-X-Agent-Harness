# Use Playwright Python image with browsers installed
FROM mcr.microsoft.com/playwright/python:v1.44.0-jammy

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency and source files
COPY pyproject.toml ./
COPY src ./src

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir .[dev]

# Copy app files
COPY mock_social ./mock_social
COPY evaluate.py ./
COPY README.md ./
COPY .env.example ./
COPY schedule.csv ./

# Create non-root user
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 CMD python -c "import sys; sys.exit(0)"

CMD ["sh", "-c", "uvicorn mock_social.mock_server:app --host 0.0.0.0 --port ${PORT:-8080}"]
