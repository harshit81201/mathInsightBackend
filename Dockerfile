# Railway-optimized Dockerfile
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Set work directory
WORKDIR /app

# Copy uv files
COPY pyproject.toml uv.lock ./

# Install dependencies using uv
RUN uv sync --frozen

# Copy project files
COPY . .

# Create directory for SQLite database
RUN mkdir -p /app/data

# Collect static files
RUN uv run python manage.py collectstatic --noinput

# Railway uses PORT environment variable
EXPOSE $PORT

# Health check for Railway
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:$PORT/admin/ || exit 1

# Railway deployment: Run migrations and start with gunicorn
CMD ["sh", "-c", "uv run python manage.py migrate && uv run gunicorn mathInsight.wsgi:application --bind 0.0.0.0:$PORT"]
