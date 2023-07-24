# Sample Dockerfile. Use platydock -c /path/to/custom/config.yaml
# to generate your custom Dockerfile.


FROM python:3.11-alpine

RUN mkdir -p /install /app
COPY . /install
RUN apk add --update --no-cache redis
RUN apk add --update --no-cache --virtual build-base g++ rust
RUN pip install -U pip
RUN cd /install && pip install .
RUN apk del build-base g++ rust

EXPOSE 8008
VOLUME /app/config
VOLUME /app/workdir

CMD python -m platypush --start-redis --config-file /app/config/config.yaml --workdir /app/workdir
