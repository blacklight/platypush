FROM alpine
ADD . /install
WORKDIR /var/lib/platypush

RUN DOCKER_CTX=1 /install/platypush/install/scripts/alpine/install.sh
RUN cd /install && pip install -U --no-input --no-cache-dir .
RUN rm -rf /install

EXPOSE 8008

VOLUME /etc/platypush
VOLUME /var/lib/platypush

CMD /run.sh
