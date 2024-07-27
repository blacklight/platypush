FROM debian

WORKDIR /var/lib/platypush

ARG DEBIAN_FRONTEND=noninteractive
ENV DEBIAN_FRONTEND=noninteractive
ARG DOCKER_CTX=1
ENV DOCKER_CTX=1

RUN --mount=type=bind,source=.,target=/curdir \
    apt update && \
    # If the current directory is the Platypush repository, then we can copy the existing files \
    if grep 'name="platypush"' /curdir/pyproject.toml >/dev/null 2>&1; \
    then \
      cp -r /curdir /install; \
    # Otherwise, we need to clone the repository \
    else \
      apt install -y git && \
      git clone https://github.com/blacklight/platypush.git /install; \
    fi

RUN /install/platypush/install/scripts/debian/install.sh && \
    cd /install && \
    pip install -U --no-input --no-cache-dir . --break-system-packages && \
    rm -rf /install && \
    rm -rf /root/.cache/pip && \
    find / | grep -E "(/__pycache__$|\.pyc$|\.pyo$)" | xargs rm -rf && \
    apt remove -y git build-essential && \
    rm -rf /var/lib/apt/lists/* && \
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
