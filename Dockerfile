# Stage 1: Builder
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Install system dependencies required for building
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code for collectstatic
COPY . .

# Install django and python-dotenv for collectstatic
RUN pip install --no-cache-dir django python-dotenv

# Collect static files
RUN PYTHONPATH=/app python manage.py collectstatic --noinput --clear || echo "Static files collection skipped"

# Stage 2: Runtime
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user for security with proper home directory
RUN groupadd -r appuser && useradd -r -g appuser -d /home/appuser -m appuser

# Set working directory
WORKDIR /app

# Copy entire app from builder with proper ownership
COPY --from=builder --chown=appuser:appuser /app /app

# Ensure app directory is writable
RUN chown -R appuser:appuser /app && chmod -R 755 /app

# Create and set writable tmp directory for gunicorn
RUN mkdir -p /tmp/gunicorn && chown -R appuser:appuser /tmp/gunicorn

# Install all Python dependencies in the runtime stage
RUN pip install --no-cache-dir -r /app/requirements.txt

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/').read()" || exit 1

# Run gunicorn with whitenoise for static files
CMD ["python", "-m", "gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-", "config.wsgi:application"]
