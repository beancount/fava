FROM python:3.6.0-alpine

ENV BEANCOUNT_INPUT_FILE ""
ENV FAVA_OPTIONS "-H 0.0.0.0"
ENV FINGERPRINT "4e:65:3e:76:0f:81:59:85:5b:50:06:0c:c2:4d:3c:56:53:8b:83:3e:9b:fa:55:26:98:9a:ca:e2:25:03:92:47"
ENV BUILDDEPS "libxml2-dev libxslt-dev gcc musl-dev mercurial git nodejs make g++"
ENV RUNDEPS "libxml2 libxslt"

RUN cd /root \
        && apk add --update $BUILDDEPS $RUNDEPS \
        && hg clone --config bitbucket.org:fingerprints=sha256:$FINGERPRINT https://bitbucket.org/blais/beancount \
        && (cd beancount && hg log -l1) \
        && rm -rf ./beancount/.hg \
        && python3 -mpip install ./beancount \
        && git clone https://github.com/beancount/fava.git \
        && (cd fava && git log -1) \
        && make -C fava \
        && make -C fava mostlyclean \
        && rm fava/CHANGES \
        && python3 -mpip install ./fava \
        && python3 -mpip uninstall --yes pip \
        && find /usr/local/lib/python3.6/site-packages -name *.so -print0|xargs -0 strip -v \
        && apk del $BUILDDEPS \
        && rm -rf /var/cache/apk/{*,.[!.]*} /tmp/{*,.[!.]*} /root/{*,.[!.]*} \
        && find /usr/local/lib/python3.6 -name __pycache__ -print0|xargs -0 rm -rf \
        && find /usr/local/lib/python3.6 -name *.pyc -print0|xargs -0 rm -f


# Default fava port number
EXPOSE 5000

CMD fava $FAVA_OPTIONS $BEANCOUNT_INPUT_FILE
