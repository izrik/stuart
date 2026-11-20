FROM python:3.11.17-alpine3.24


RUN mkdir -p /opt/stuart

WORKDIR /opt/stuart

COPY requirements.txt \
     ./

# Alpine packages are left unpinned (DL3018): the Alpine repositories drop
# old package versions, so a pin would break future builds. The build tooling
# (DL3013) tracks the latest release on purpose.
# hadolint ignore=DL3018,DL3013
RUN apk add --no-cache git bash libpq && \
    pip install --no-cache-dir --upgrade pip setuptools wheel
# PIP_NO_CACHE_DIR also reaches the pip that build isolation starts for
# source packages, which --no-cache-dir alone does not.
# hadolint ignore=DL3018
RUN apk add --no-cache --virtual .build-deps gcc musl-dev libffi-dev postgresql-dev g++ && \
    PIP_NO_CACHE_DIR=1 pip install --no-cache-dir gunicorn==27.0.1 \
                psycopg2==2.9.13 \
                -r requirements.txt && \
    apk --no-cache --purge del .build-deps

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
ENV STUART_VERSION="$VERSION" \
    STUART_REVISION="$REVISION"
LABEL org.opencontainers.image.version=$VERSION \
      org.opencontainers.image.revision=$REVISION
# These keys predate the lowercase convention (DL3048); renaming them would
# break anything that already reads them.
# hadolint ignore=DL3048
LABEL \
    Name="stuart" \
    Version="$STUART_VERSION" \
    Summary="A Python wiki system." \
    Description="A Python wiki system." \
    maintaner="izrik <izrik@izrik.com>"

CMD ["/opt/stuart/docker_start.sh"]
