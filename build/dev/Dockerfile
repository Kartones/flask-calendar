FROM flask-calendar:base

ARG uid=1000
ARG gid=1000

USER root

COPY requirements-dev.txt /code
RUN pip install -r /code/requirements-dev.txt

USER $uid

VOLUME /code
WORKDIR /code
