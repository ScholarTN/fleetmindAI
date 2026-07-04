FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements/base.txt .
RUN pip install --no-cache-dir -r base.txt

COPY . .

EXPOSE 8000
