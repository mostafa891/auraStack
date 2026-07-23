# ==============================================================================
# Stage 1: Build Vue/Vite assets
# ==============================================================================
FROM node:20-alpine AS frontend-builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --prefer-offline --no-audit
COPY frontend/ ./frontend/
COPY static/ ./static/
RUN npm run build

# ==============================================================================
# Stage 2: Build Python environment and runtime
# ==============================================================================
FROM python:3.13-slim AS runner

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DJANGO_SETTINGS_MODULE=core.settings.production \
    PORT=8000

# Set working directory
WORKDIR /app

# Install runtime and compiler dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create a non-privileged user (OWASP / Docker security best practice)
RUN groupadd -g 10001 appuser && \
    useradd -u 10000 -g appuser -m -s /sbin/nologin appuser

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy all project files first
COPY . .

# Copy Vite build output (overwriting local static/dist)
COPY --from=frontend-builder /app/static/dist ./static/dist

# Set correct ownership for security
RUN chown -R appuser:appuser /app

# Switch to the non-privileged user
USER appuser

# Collect static files (needs a dummy DATABASE_URL to pass Django settings checks during build)
RUN DATABASE_URL=postgres://dummy:dummy@localhost:5432/dummy python manage.py collectstatic --noinput

# Health check with proper endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl --fail http://localhost:${PORT}/health/ || exit 1

# Run application using gunicorn with dynamic worker scaling & graceful shutdown
EXPOSE 8000
CMD ["sh", "-c", "python manage.py migrate && gunicorn core.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers ${WEB_WORKERS:-4} --threads ${WEB_THREADS:-2} --timeout 60 --graceful-timeout 30 --access-logformat '%(h)s %(l)s %(u)s %(t)s \"%(r)s\" %(s)s %(b)s \"%(f)s\" \"%(a)s\"'"]
