FROM alpine

ADD . /install
WORKDIR /var/lib/platypush

ARG DOCKER_CTX=1
ENV DOCKER_CTX=1

RUN apk update
RUN /install/platypush/install/scripts/alpine/install.sh
RUN cd /install && pip install -U --no-input --no-cache-dir .
RUN rm -rf /install
RUN rm -rf /var/cache/apk

EXPOSE 8008

VOLUME /etc/platypush
VOLUME /var/lib/platypush

CMD platypush \
  --start-redis \
  --config /etc/platypush/config.yaml \
  --workdir /var/lib/platypush
