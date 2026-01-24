FROM python:slim as builder

RUN pip install --root-user-action ignore uv && \
    uv pip install --system --prefix="/install" rustfava

FROM python:slim

COPY --from=builder /install /usr/local

ENV RUSTFAVA_HOST "0.0.0.0"
EXPOSE 5000
CMD rustfava
