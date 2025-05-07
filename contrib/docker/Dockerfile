FROM python:slim as builder

RUN pip install --root-user-action ignore --prefix="/install" fava

FROM python:slim

COPY --from=builder /install /usr/local

ENV FAVA_HOST "0.0.0.0"
EXPOSE 5000
CMD fava
