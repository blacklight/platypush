FROM alpine

ADD . /install
WORKDIR /var/lib/platypush

ARG DOCKER_CTX=1
ENV DOCKER_CTX=1

RUN apk update && \
    /install/platypush/install/scripts/alpine/install.sh && \
    cd /install && pip install -U --no-input --no-cache-dir . --break-system-packages && \
    rm -rf /install && \
    apk cache clean

EXPOSE 8008

VOLUME /etc/platypush
VOLUME /var/lib/platypush
VOLUME /var/cache/platypush

CMD platypush \
  --start-redis \
  --config /etc/platypush/config.yaml \
  --workdir /var/lib/platypush \
  --cachedir /var/cache/platypush
