# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Stuart** is a Python wiki system built on Flask. It provides a simple web-based wiki with user authentication, Markdown/GFM content rendering, tagging, and SQLAlchemy-based persistence. The entire application lives in a single file (`stuart.py`) with Jinja2 templates for the UI.

## Commands

Stuart targets Python 3.11 — the version the [`Dockerfile`](Dockerfile) and
[`.github/workflows/ci.yml`](.github/workflows/ci.yml) pin. Every version in
`requirements.txt` is pinned exactly, including `Werkzeug` and `Markdown`,
whose newer releases have dropped APIs that Flask 2.0.1 and py-gfm 1.0.2
still import. Don't upgrade either on its own.

```bash
# Setup
python3.11 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt

# Run the wiki
python stuart.py --db-uri "sqlite:///wiki.db" --create-db

# Run tests
python run_tests.py

# Full lint and test suite (requires both Python and npm deps)
./run_tests_with_coverage.sh

# The checks CI gates pull requests with, individually
python run_tests.py
flake8 stuart.py run_tests.py
shellcheck run_tests_with_coverage.sh
npm ci
./node_modules/.bin/markdownlint README.md
./node_modules/.bin/csslint static/stuart.css
./node_modules/.bin/dockerlint Dockerfile

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
3. Run tests: `python run_tests.py`. Better, run the whole local gate,
   `./run_tests_with_coverage.sh`, which is what CI checks (minus the two
   steps that need credentials — see *Continuous integration* below).
4. Commit with a descriptive message. Add an entry under `## [Unreleased]` in [CHANGELOG.md](CHANGELOG.md) for anything a user or operator would notice — a new command, a changed default, a new environment variable, a fixed bug. Internal refactors with no outward effect need none.
5. Push and open a pull request against `master`
6. Address review feedback

## Continuous Integration

Every pull request, and every push to `master`, is gated by
[`.github/workflows/ci.yml`](.github/workflows/ci.yml). It runs each of these
as a separate check, so a failure names itself:

| Check | Command |
| --- | --- |
| Python tests | `python run_tests.py` |
| Lint Python | `flake8 stuart.py run_tests.py` |
| Lint shell | `shellcheck run_tests_with_coverage.sh` |
| Lint Markdown | `./node_modules/.bin/markdownlint README.md` |
| Lint CSS | `./node_modules/.bin/csslint static/stuart.css` |
| Lint Dockerfile | `./node_modules/.bin/dockerlint Dockerfile` |

These are the same commands [`run_tests_with_coverage.sh`](run_tests_with_coverage.sh)
chains, so running that script locally covers all of them. To reproduce the
checks one at a time, install the Python dependencies
(`pip install -r requirements.txt -r dev_requirements.txt`) and the npm
linters (`npm ci`), then run the commands in the table above.

Two steps of the local script are deliberately *not* in CI: `safety check`
needs an account with an external service, and `coveralls` needs a repository
token. `coverage html` is skipped too — it only writes a local HTML report.

## Security

[SECURITY.md](SECURITY.md) is where a vulnerability report goes: GitHub's
private vulnerability reporting, or the maintainer directly — not a public
issue. If you find a security problem in this repository while working on
something else, that's the path for it, and the finding doesn't belong in a
commit message or a public issue until it's fixed.

Two things follow from that for ordinary changes:

- **Never commit a credential**, not even an expired or obviously fake one
  in a test fixture. `.gitignore` already covers `.env` and local `*.db`
  files; example and config values stay placeholders.
- **Workflows get the narrowest token that works.**
  [`.github/workflows/ci.yml`](.github/workflows/ci.yml) declares
  `permissions: contents: read` at the top level. A job that needs more
  gets its own `permissions:` block with just what it needs, rather than
  widening the top-level one. Don't interpolate untrusted text — a pull
  request title, a branch name, an issue body — into a `run:` step; pass it
  through `env:` and reference the variable.

Dependabot watches `requirements.txt`, `dev_requirements.txt` and
`package.json` weekly ([`.github/dependabot.yml`](.github/dependabot.yml)).
There is no `pip-audit` job in CI yet — see
[#53](https://github.com/izrik/stuart/issues/53), which has to clear the
open advisories against the current pins first.

## Further Documentation

- [Configuration](docs/configuration.md) — all environment variables and CLI options
- [Changelog](CHANGELOG.md) — what changed in each release
- [Security policy](SECURITY.md) — how to report a vulnerability
