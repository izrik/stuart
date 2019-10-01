FROM python:3.7.4-alpine3.10

ENV STUART_VERSION=0.1
LABEL \
    Name="stuart" \
    Version="$STUART_VERSION" \
    Summary="A Python wiki system." \
    Description="A Python wiki system." \
    maintaner="izrik <izrik@izrik.com>"

RUN mkdir -p /opt/stuart

WORKDIR /opt/stuart

RUN apk add --no-cache bash

RUN apk add --virtual .build-deps gcc musl-dev libffi-dev mariadb-dev && \
    pip install gunicorn==19.8.1    --no-cache-dir && \
    pip install mysqlclient==1.4.4  --no-cache-dir && \
    apk --purge del .build-deps

COPY requirements.txt ./

RUN apk add --virtual .build-deps gcc musl-dev libffi-dev && \
    pip install -r requirements.txt     --no-cache-dir && \
    apk --purge del .build-deps

COPY stuart.py \
     LICENSE \
     README.md \
     docker_start.sh \
     ./

COPY static static
COPY templates templates

EXPOSE 8080
ENV STUART_PORT=8080 \
    STUART_HOST=0.0.0.0

CMD ["/opt/stuart/docker_start.sh"]
