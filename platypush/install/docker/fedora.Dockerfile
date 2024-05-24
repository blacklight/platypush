FROM fedora

ADD . /install
WORKDIR /var/lib/platypush

ARG DOCKER_CTX=1
ENV DOCKER_CTX=1

# Enable the RPM Fusion repository
RUN dnf install -y https://download1.rpmfusion.org/free/fedora/rpmfusion-free-release-$(rpm -E %fedora).noarch.rpm && \
  /install/platypush/install/scripts/fedora/install.sh && \
  cd /install && \
  pip install -U --no-input --no-cache-dir . --break-system-packages && \
  rm -rf /install && \
  dnf clean all -y

EXPOSE 8008

VOLUME /etc/platypush
VOLUME /var/lib/platypush
VOLUME /var/cache/platypush

CMD platypush \
  --start-redis \
  --config /etc/platypush/config.yaml \
  --workdir /var/lib/platypush \
  --cachedir /var/cache/platypush
