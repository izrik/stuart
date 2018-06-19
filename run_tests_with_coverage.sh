#!/bin/bash

coverage run --source=stuart ./run_tests.py "$@" && \
    coverage html && \
    flake8 stuart.py run_tests.py && \
    shellcheck run_tests_with_coverage.sh && \
    markdownlint README.md && \
    csslint static/stuart.css && \
    safety check && \
    echo Success
