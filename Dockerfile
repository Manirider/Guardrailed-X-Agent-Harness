# Use Playwright Python image with browsers installed
FROM mcr.microsoft.com/playwright/python:v1.44.0-jammy

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files
COPY pyproject.toml ./

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir .[dev]

# Copy source code
COPY src ./src
COPY mock_social ./mock_social
COPY evaluate.py ./
COPY README.md ./
COPY .env.example ./

# Create non-root user
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 CMD python -c "import sys; sys.exit(0)"

CMD ["python", "-m", "harness.cli"]
