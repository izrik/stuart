# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Stuart** is a Python wiki system built on Flask. It provides a simple web-based wiki with user authentication, Markdown/GFM content rendering, tagging, and SQLAlchemy-based persistence. The entire application lives in a single file (`stuart.py`) with Jinja2 templates for the UI.

## Commands

```bash
# Setup
python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt

# Run the wiki
python stuart.py --db-uri "sqlite:///wiki.db" --create-db

# Run tests
python run_tests.py

# Full lint and test suite (requires both Python and npm deps)
./run_tests_with_coverage.sh

# Docker build and run
docker build -t stuart . && docker run -p 8080:8080 stuart
```

## Architecture

```
stuart.py          # Flask app: models (User, Page, Tag, Option), routes, CLI
run_tests.py       # Unit tests using unittest
templates/         # Jinja2 HTML templates
  base.html        # Base layout with navbar
  page.html        # Single page view
  edit.html        # Page editor
  index.html       # Homepage
static/            # CSS (Bootstrap + stuart.css)
```

**Data models:**
- `User` — email/password auth via Flask-Login + bcrypt
- `Page` — wiki page with title, slug, content, summary, tags, private flag
- `Tag` — content categorization, many-to-many with Page
- `Option` — key-value settings stored in the database

**Request flow:** Routes render Jinja2 templates with Page/Tag data. Content is rendered as GitHub Flavored Markdown via `py-gfm`. Login required for page creation/editing.

## Code Style

- Standard Python conventions (PEP 8)
- 4-space indentation
- Flake8 for linting

## Branch Naming and Development Workflow

1. Create a feature branch from `master` (use hyphens, not slashes: `feature-my-feature`)
2. Implement the change
3. Run tests: `python run_tests.py`
4. Commit with a descriptive message. Add an entry under `## [Unreleased]` in [CHANGELOG.md](CHANGELOG.md) for anything a user or operator would notice — a new command, a changed default, a new environment variable, a fixed bug. Internal refactors with no outward effect need none.
5. Push and open a pull request against `master`
6. Address review feedback

## Further Documentation

- [Configuration](docs/configuration.md) — all environment variables and CLI options
- [Changelog](CHANGELOG.md) — what changed in each release
