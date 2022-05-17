FROM python:3.8.12-alpine3.14

ENV STUART_VERSION=0.6
LABEL \
    Name="stuart" \
    Version="$STUART_VERSION" \
    Summary="A Python wiki system." \
    Description="A Python wiki system." \
    maintaner="izrik <izrik@izrik.com>"

RUN mkdir -p /opt/stuart

WORKDIR /opt/stuart

COPY requirements.txt \
     ./

RUN apk add git bash libpq
RUN pip install --upgrade pip setuptools wheel
RUN apk add --virtual .build-deps gcc musl-dev libffi-dev postgresql-dev g++ && \
    pip install gunicorn==20.1.0 \
                psycopg2==2.8.6 \
                -r requirements.txt && \
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
