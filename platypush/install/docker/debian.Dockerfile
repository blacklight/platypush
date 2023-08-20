FROM debian

ADD . /install
WORKDIR /var/lib/platypush

ARG DEBIAN_FRONTEND=noninteractive
ENV DEBIAN_FRONTEND=noninteractive
ARG DOCKER_CTX=1
ENV DOCKER_CTX=1

RUN apt update
RUN /install/platypush/install/scripts/debian/install.sh
RUN cd /install && pip install -U --no-input --no-cache-dir . --break-system-packages
RUN rm -rf /install
RUN apt autoclean -y
RUN apt autoremove -y
RUN apt clean

EXPOSE 8008

VOLUME /etc/platypush
VOLUME /var/lib/platypush

CMD platypush \
  --start-redis \
  --config /etc/platypush/config.yaml \
  --workdir /var/lib/platypush
