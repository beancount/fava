# Multi-stage build for minimal image size
FROM python:3.13-alpine AS builder

# Install build dependencies
RUN apk add --no-cache gcc musl-dev

# Install uv and rustfava
RUN pip install --no-cache-dir uv && \
    uv pip install --system --prefix="/install" rustfava

# Final stage - minimal runtime image
FROM python:3.13-alpine

# Copy installed packages from builder
COPY --from=builder /install /usr/local

ENV RUSTFAVA_HOST="0.0.0.0"
EXPOSE 5000
CMD ["rustfava"]
