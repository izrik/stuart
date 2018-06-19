FROM python:2.7

ENV STUART_VERSION=0.1
LABEL \
    Name="stuart" \
    Version="$STUART_VERSION" \
    Summary="A Python wiki system." \
    Description="A Python wiki system." \
    maintaner="izrik <izrik@izrik.com>"

RUN mkdir -p /opt/stuart

WORKDIR /opt/stuart

COPY stuart.py \
     LICENSE \
     README.md \
     requirements.txt \
     docker_start.sh \
     ./

COPY static static
COPY templates templates

RUN pip install -r requirements.txt
RUN pip install gunicorn==19.8.1
RUN pip install MySQL-python==1.2.5

EXPOSE 8080
ENV STUART_PORT=8080 \
    STUART_HOST=0.0.0.0

CMD ["/opt/stuart/docker_start.sh"]
