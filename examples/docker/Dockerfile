FROM alpine
ADD . /install

RUN apk add --update --no-interactive --no-cache \
    python3 \
    py3-pip \
    py3-alembic \
    py3-bcrypt \
    py3-dateutil \
    py3-docutils \
    py3-flask \
    py3-frozendict \
    py3-greenlet \
    py3-magic \
    py3-mypy-extensions \
    py3-psutil \
    py3-redis \
    py3-requests \
    py3-rsa \
    py3-sqlalchemy \
    py3-tornado \
    py3-typing-extensions \
    py3-tz \
    py3-websocket-client \
    py3-websockets \
    py3-wheel \
    py3-yaml \
    py3-zeroconf \
    redis

RUN cd /install && pip install --no-cache-dir .
RUN cd / && rm -rf /install

EXPOSE 8008
VOLUME /app/config
VOLUME /app/workdir

CMD platypush --start-redis --config /app/config/config.yaml --workdir /app/workdir
