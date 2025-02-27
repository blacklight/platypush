FROM ubuntu

WORKDIR /var/lib/platypush

ARG DEBIAN_FRONTEND=noninteractive
ENV DEBIAN_FRONTEND=noninteractive
ARG DOCKER_CTX=1
ENV DOCKER_CTX=1

RUN --mount=type=bind,source=.,target=/curdir \
    apt update && \
    # If the current directory is the Platypush repository, then we can copy the existing files \
    if grep -E 'name\s*=\s*"platypush"' /curdir/pyproject.toml >/dev/null 2>&1; \
    then \
      cp -r /curdir /install; \
    # Otherwise, we need to clone the repository \
    else \
      apt install -y git && \
      git clone https://github.com/blacklight/platypush.git /install; \
    fi

RUN /install/platypush/install/scripts/debian/install.sh && \
    cd /install && \
    pip install -U --no-input --no-cache-dir --no-deps --ignore-installed --break-system-packages . && \
    rm -rf /install && \
    rm -rf /root/.cache && \
    apt remove -y git \
      build-essential \
      docutils-common \
      fonts-dejavu-mono \
      manpages \
      manpages-dev \
      python-babel-localedata && \
    apt autoclean -y && \
    apt autoremove -y && \
    apt clean && \
    rm -rf /var/cache/apt/* && \
    rm -rf /tmp/* && \
    find / | grep -E "(/__pycache__$|\.pyc$|\.pyo$)" | xargs rm -rf

EXPOSE 8008

VOLUME /etc/platypush
VOLUME /var/lib/platypush
VOLUME /var/cache/platypush

CMD platypush \
  --start-redis \
  --config /etc/platypush/config.yaml \
  --workdir /var/lib/platypush \
  --cachedir /var/cache/platypush
