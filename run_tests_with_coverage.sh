#!/bin/bash

coverage run --source=stuart ./run_tests.py "$@" && \
    coverage html
