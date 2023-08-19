FROM debian
ADD . /install
WORKDIR /var/lib/platypush

RUN apt update
RUN DOCKER_CTX=1 /install/platypush/install/scripts/debian/install.sh
RUN cd /install && pip install -U --no-input --no-cache-dir .
RUN rm -rf /install
RUN apt autoclean -y
RUN apt autoremove -y
RUN apt clean

EXPOSE 8008

VOLUME /etc/platypush
VOLUME /var/lib/platypush

CMD /run.sh
