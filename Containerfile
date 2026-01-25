# Stage 1: Build frontend and Python package
FROM node:22-slim AS builder

ARG VERSION=0.0.0
ENV SETUPTOOLS_SCM_PRETEND_VERSION=${VERSION}

WORKDIR /app

# Install Python and uv
RUN apt-get update && apt-get install -y --no-install-recommends python3 python3-venv && rm -rf /var/lib/apt/lists/*
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Install frontend dependencies first (better layer caching)
COPY frontend/package.json frontend/package-lock.json ./frontend/
RUN cd frontend && npm ci

# Copy all source files
COPY . .

# Build frontend
RUN cd frontend && npm run build

# Build wheel
RUN uv build --wheel --out-dir /dist

# Stage 2: Runtime
FROM python:3.13-slim

# Install the wheel
COPY --from=builder /dist/*.whl /tmp/
RUN pip install --no-cache-dir /tmp/*.whl && rm /tmp/*.whl

# Configure runtime
ENV FAVA_HOST="0.0.0.0"
EXPOSE 5000

# Run as non-root user
RUN useradd --create-home fava
USER fava
WORKDIR /home/fava

CMD ["fava"]
