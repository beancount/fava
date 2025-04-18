FROM python:alpine as builder

RUN apk add --update libxml2-dev libxslt-dev gcc musl-dev g++ bison flex
RUN pip install --root-user-action ignore --prefix="/install" fava

FROM python:alpine

COPY --from=builder /install /usr/local

ENV FAVA_HOST "0.0.0.0"
EXPOSE 5000
CMD fava
