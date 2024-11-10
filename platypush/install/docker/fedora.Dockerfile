FROM fedora

WORKDIR /var/lib/platypush

ARG DOCKER_CTX=1
ENV DOCKER_CTX=1

RUN --mount=type=bind,source=.,target=/curdir \
    # If the current directory is the Platypush repository, then we can copy the existing files \
    if grep -E 'name\s*=\s*"platypush"' /curdir/pyproject.toml >/dev/null 2>&1; \
    then \
      cp -r /curdir /install; \
    # Otherwise, we need to clone the repository \
    else \
      dnf install -y git && \
      git clone https://github.com/blacklight/platypush.git /install; \
    fi; \
    dnf install -y https://download1.rpmfusion.org/free/fedora/rpmfusion-free-release-$(rpm -E %fedora).noarch.rpm

RUN /install/platypush/install/scripts/fedora/install.sh && \
  cd /install && \
  pip install -U --no-input --no-cache-dir --no-deps --ignore-installed --break-system-packages . && \
  rm -rf /install && \
  rm -rf /root/.cache && \
  dnf remove -y build-essential git && \
  dnf clean all -y && \
  rm -rf /var/cache/dnf/* && \
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
