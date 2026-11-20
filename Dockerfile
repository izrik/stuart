FROM python:3.11.17-alpine3.24


RUN mkdir -p /opt/stuart

WORKDIR /opt/stuart

COPY requirements.txt \
     ./

RUN apk add git bash libpq
RUN pip install --upgrade pip setuptools wheel
RUN apk add --virtual .build-deps gcc musl-dev libffi-dev postgresql-dev g++ && \
    pip install gunicorn==20.1.0 \
                psycopg2==2.9.10 \
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

# Record what was built. `build_docker.sh` passes both as --build-arg; they
# come last so a new version does not invalidate the layers above. The
# STUART_* variables let the running app report its own version, and the
# labels let anything inspecting the image read it without starting it.
ARG VERSION
ARG REVISION
ENV STUART_VERSION=$VERSION \
    STUART_REVISION=$REVISION
LABEL org.opencontainers.image.version=$VERSION \
      org.opencontainers.image.revision=$REVISION
LABEL \
    Name="stuart" \
    Version="$STUART_VERSION" \
    Summary="A Python wiki system." \
    Description="A Python wiki system." \
    maintaner="izrik <izrik@izrik.com>"

CMD ["/opt/stuart/docker_start.sh"]
