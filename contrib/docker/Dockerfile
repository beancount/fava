# Multi-stage build for minimal image size
FROM python:3.13-alpine AS builder

# Install build dependencies
RUN apk add --no-cache gcc musl-dev

# Install uv and rustfava
RUN pip install --no-cache-dir uv && \
    uv pip install --system --prefix="/install" rustfava

# Final stage - minimal runtime image
FROM python:3.13-alpine

LABEL org.opencontainers.image.source="https://github.com/rustledger/rustfava"
LABEL org.opencontainers.image.description="Web interface for rustledger"
LABEL org.opencontainers.image.licenses="MIT"

# Create non-root user for security
RUN addgroup -S rustfava && adduser -S rustfava -G rustfava

# Copy installed packages from builder
COPY --from=builder /install /usr/local

USER rustfava

ENV RUSTFAVA_HOST="0.0.0.0"
EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000')" || exit 1

CMD ["rustfava"]
