# Fava Docker image replicating local steps:
# 1) python3 -m venv .venv
# 2) source .venv/bin/activate
# 3) pip install fava
# 4) fava contrib/examples/example.beancount
#
# Build:
#   docker build -t fava-app:latest .
# Run with built-in example:
#   docker run -it --rm -p 5000:5000 fava-app:latest
# Run with your own ledger mounted:
#   docker run -it --rm -p 5000:5000 \
#     -v "$PWD/data:/data" \
#     -e LEDGER_FILE=/data/ledger.beancount \
#     fava-app:latest

FROM python:3.11-slim

ARG PIP_NO_CACHE_DIR=1

# Install minimal tools
RUN apt-get update && apt-get install -y --no-install-recommends \
      git curl tini \
    && rm -rf /var/lib/apt/lists/*

# Create app and data dirs, non-root user
RUN useradd -u 10001 -m appuser
RUN mkdir -p /app /data /opt && chown -R appuser:appuser /app /data /opt
USER appuser
WORKDIR /app

# Create venv exactly like local steps
RUN python3 -m venv /app/.venv

# Activate venv for all subsequent RUN/CMD via ENV PATH
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="${VIRTUAL_ENV}/bin:${PATH}"

# Clone your fork to provide contrib/examples/example.beancount
RUN git clone --depth=1 https://github.com/ahdsab/Fava.git /opt/fava

# Install fava inside venv
RUN pip install --no-cache-dir fava

# Defaults (can be overridden)
ENV FAVA_HOST=0.0.0.0 \
    FAVA_PORT=5000 \
    LEDGER_FILE="" \
    FAVA_OPTIONS=""

# Entry script (activates venv implicitly via PATH and runs fava)
COPY --chown=appuser:appuser entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

EXPOSE 5000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --retries=6 CMD curl -fsS "http://localhost:${FAVA_PORT}/" >/dev/null || exit 1

ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["/app/entrypoint.sh"]
