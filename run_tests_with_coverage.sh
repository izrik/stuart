#!/bin/bash

coverage run --source=wikiware ./run_tests.py "$@" && \
    coverage html
