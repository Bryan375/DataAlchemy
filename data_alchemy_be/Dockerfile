FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /code

# Install dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        postgresql-client \
        gcc \
        python3-dev \
        libpq-dev \
        netcat-traditional && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt /code/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /code/

