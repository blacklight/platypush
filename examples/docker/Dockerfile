# Sample Dockerfile. Use platydock -c /path/to/custom/config.yaml
# to generate your custom Dockerfile.


FROM python3.11:alpine

RUN mkdir -p /install /app
COPY . /install
RUN cd /install
RUN apk add --update --no-cache redis
RUN apk add --update --no-cache --virtual build-base g++ rust
RUN pip install -U pip
RUN pip install .
RUN apk del build-base g++ rust
RUN cd /app && python setup.py build install

EXPOSE 8008
VOLUME /app/config
VOLUME /app/workdir

CMD python -m platypush --start-redis --config-file /app/config/config.yaml --workdir /app/workdir
