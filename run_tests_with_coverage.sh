#!/bin/bash

coverage run --source=stuart ./run_tests.py "$@" && \
    coverage html && \
    flake8 stuart.py run_tests.py && \
    shellcheck run_tests_with_coverage.sh && \
    ./node_modules/.bin/markdownlint README.md && \
    ./node_modules/.bin/csslint static/stuart.css && \
    pip-audit -r requirements.txt -r dev_requirements.txt && \
    ./node_modules/.bin/dockerlint Dockerfile && \
  echo Success
