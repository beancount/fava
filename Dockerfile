# rustfava server - web interface for rustledger
# Build: docker build -t rustfava .
# Run:   docker run -p 5000:5000 -v /path/to/ledger:/data rustfava /data/main.beancount

FROM python:3.13-slim

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    unzip \
    xz-utils

# Install wasmtime (direct binary download)
ARG WASMTIME_VERSION=v29.0.1
RUN curl -L "https://github.com/bytecodealliance/wasmtime/releases/download/${WASMTIME_VERSION}/wasmtime-${WASMTIME_VERSION}-x86_64-linux.tar.xz" -o /tmp/wasmtime.tar.xz \
    && tar -xf /tmp/wasmtime.tar.xz -C /tmp \
    && mv /tmp/wasmtime-${WASMTIME_VERSION}-x86_64-linux/wasmtime /usr/local/bin/wasmtime \
    && chmod +x /usr/local/bin/wasmtime \
    && rm -rf /tmp/wasmtime*

# Install bun (for frontend build)
RUN curl -fsSL https://bun.sh/install | bash \
    && ln -s /root/.bun/bin/bun /usr/local/bin/bun

WORKDIR /app

# Copy source and frontend (needed for build backend)
COPY pyproject.toml .
COPY _build_backend.py .
COPY src/ src/
COPY frontend/ frontend/

# Install rustfava (set version since no .git in container)
ARG VERSION=0.1.0
ENV SETUPTOOLS_SCM_PRETEND_VERSION=${VERSION}
RUN pip install --no-cache-dir .

# Cleanup build dependencies
RUN apt-get purge -y curl unzip xz-utils \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf frontend/ \
    && rm -rf /root/.bun

# Create data directory for mounting ledger files
RUN mkdir -p /data

EXPOSE 5000

# Default: listen on all interfaces for container access
ENV RUSTFAVA_HOST=0.0.0.0
ENV RUSTFAVA_PORT=5000

ENTRYPOINT ["rustfava"]
# User provides the beancount file path as argument, e.g.:
# docker run -p 5000:5000 -v ~/ledger:/data rustfava /data/main.beancount
