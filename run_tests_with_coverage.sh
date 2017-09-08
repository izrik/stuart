#!/bin/bash

coverage run --source=blogware ./run_tests.py "$@" && \
    coverage html
