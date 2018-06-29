#!/bin/sh

python /opt/stuart/stuart.py --create-db
gunicorn -b $STUART_HOST:$STUART_PORT stuart:gapp
