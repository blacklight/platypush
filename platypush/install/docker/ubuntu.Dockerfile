FROM ubuntu

ADD . /install
WORKDIR /var/lib/platypush

ARG DEBIAN_FRONTEND=noninteractive
ENV DEBIAN_FRONTEND=noninteractive
ARG DOCKER_CTX=1
ENV DOCKER_CTX=1

RUN apt update && \
    /install/platypush/install/scripts/debian/install.sh && \
    cd /install && pip install -U --no-input --no-cache-dir . && \
    rm -rf /install && \
    apt autoclean -y && \
    apt autoremove -y && \
    apt clean

EXPOSE 8008

VOLUME /etc/platypush
VOLUME /var/lib/platypush
VOLUME /var/cache/platypush

CMD platypush \
  --start-redis \
  --config /etc/platypush/config.yaml \
  --workdir /var/lib/platypush \
  --cachedir /var/cache/platypush
