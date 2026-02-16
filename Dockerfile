FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    mariadb-client-compat \
    libmariadb-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/

# Create migrations directory if it doesn't exist
RUN mkdir -p /app/articles/migrations && touch /app/articles/migrations/__init__.py
RUN mkdir -p /app/users/migrations && touch /app/users/migrations/__init__.py
RUN mkdir -p /app/profiles/migrations && touch /app/profiles/migrations/__init__.py

# Run migrations and collect static files
RUN python manage.py collectstatic --noinput || true

# Expose port
EXPOSE 8000

# Run gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--timeout", "120", "conduit.wsgi:application"]
