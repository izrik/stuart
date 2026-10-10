# Changelog

All notable changes to Stuart are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

Documentation: the repository now explains itself, to contributors and to AI
coding agents, and records what changed in each release.

### Added

- **Documentation for contributors and coding agents**
  ([#36](https://github.com/izrik/stuart/issues/36),
  [#37](https://github.com/izrik/stuart/pull/37)).
  [`CLAUDE.md`](CLAUDE.md), with `AGENTS.md` as a symlink to it, describes
  the project layout, the commands to set up and run and test it, the data
  model, and the branch-naming and development workflow.
  [`docs/configuration.md`](docs/configuration.md) documents every
  `STUART_*` environment variable and every command-line argument, including
  the admin commands and the defaults the Docker image overrides — none of
  which was written down anywhere before. The `README.md` gained a quick
  start, a feature list, a table of the common settings and Docker
  instructions.

- **This changelog**
  ([#38](https://github.com/izrik/stuart/issues/38)). What changed between
  releases was previously recorded only in GitHub Releases and the git log.

### Changed

- GitPython upgraded from 3.1.18 to 3.1.31
  ([#34](https://github.com/izrik/stuart/pull/34)). Stuart uses it only to
  report the git revision in the page footer, and treats it as optional, but
  3.1.31 is what the Docker image installs.

## [v0.7] - 2022-05-16

Logging in becomes per-user. The single site-wide password is replaced by
user accounts kept in the database, and a Docker image that could not reach
a PostgreSQL server at all is fixed. The version number went from 0.5
straight to 0.7; there is no v0.6 release.

### Added

- **User accounts** ([#31](https://github.com/izrik/stuart/pull/31)). A user
  is now a row in the database with an email address and a bcrypt-hashed
  password, and the login form asks for both. More than one person can have
  an account, and a password can be changed or revoked for one of them
  without affecting the others.

- **`--create-user EMAIL PASSWORD`** creates an account from the command
  line ([#31](https://github.com/izrik/stuart/pull/31)).

- **A usable account on a fresh database.** `--create-db` now creates a
  `root` user with a random 32-character password and prints it to the
  console, so a new install can be logged into without a separate setup step
  ([#31](https://github.com/izrik/stuart/pull/31)).

### Changed

- Dependencies upgraded: Flask-Bcrypt 0.7.1 to 1.0.1, Flask-Login 0.5.0 to
  0.6.1 and Flask-WTF 0.15.1 to 1.0.1, and, among the lint tooling,
  `markdownlint-cli` 0.28.1 to 0.31.1 and `minimist` 1.2.5 to 1.2.6
  ([#29](https://github.com/izrik/stuart/pull/29),
  [#30](https://github.com/izrik/stuart/pull/30)).

### Removed

- **The site-wide password.** The bcrypt hash stored as the
  `hashed_password` option in the database is no longer consulted
  ([#31](https://github.com/izrik/stuart/pull/31)). An existing install has
  to create at least one user — `--create-user`, or `--create-db` against
  the existing database, which adds the `root` user and leaves the pages
  alone — because the old password will no longer log anyone in.
  `--hash-password` still prints a hash, for setting a password by hand.

### Fixed

- **A PostgreSQL-backed container no longer fails on startup**
  ([#28](https://github.com/izrik/stuart/pull/28)). The image built
  `psycopg2` against `postgresql-dev` and then purged the build
  dependencies, which took `libpq` with them, so the driver had nothing to
  load at runtime and every connection attempt failed. `libpq` is now
  installed as a runtime package.

- **A session now identifies whoever logged in.** Restoring a session looks
  the user up in the database; previously it fabricated a user from the
  configured author name, so the logged-in identity was the site's author
  rather than the person holding the session
  ([#31](https://github.com/izrik/stuart/pull/31)).

## [v0.5] - 2021-09-06

The database connection URI can come from a file instead of an environment
variable, and the configured homepage works for the first time.

### Added

- **`STUART_DB_URI_FILE` and `--db-uri-file PATH`**
  ([#26](https://github.com/izrik/stuart/pull/26)) — read the database
  connection URI from a file. The credentials in it stay out of the process
  environment, and an orchestrator can mount the file as a secret.
  `STUART_DB_URI` still takes precedence when both are set. A missing or
  unreadable file is reported as a configuration error naming the path,
  rather than failing later with a connection error.

### Changed

- **There is no longer a default database.** `STUART_DB_URI` used to default
  to `sqlite:////tmp/wiki.db`. With neither it nor `STUART_DB_URI_FILE` set,
  Stuart now runs against an in-memory SQLite database whose contents are
  gone when the process exits
  ([#26](https://github.com/izrik/stuart/pull/26)). Anyone who relied on the
  old default — including anyone whose wiki was in `/tmp` — has to pass the
  URI explicitly.

- **Tables are created on startup**, not only under `--create-db`
  ([#27](https://github.com/izrik/stuart/pull/27)), so running under
  Gunicorn — which never reaches the `--create-db` code path — works against
  an empty database.

- The Docker image installs its dependencies before copying the application
  code, so editing `stuart.py` no longer invalidates the dependency layer
  and a rebuild takes seconds instead of minutes
  ([#27](https://github.com/izrik/stuart/pull/27)).

- Under `--debug`, startup additionally prints the URI file path and the
  effective database URI resolved from it
  ([#26](https://github.com/izrik/stuart/pull/26)).

### Fixed

- **Setting `main_page` to a page's title now shows that page on the
  homepage** ([#26](https://github.com/izrik/stuart/pull/26)). The title
  lookup filtered on `title`, a Python property rather than the mapped
  column, and so silently matched nothing; only the slug fallback worked, so
  `--set-option main_page "Page Title"` left the default index showing. The
  feature had never worked with a title since it was added in v0.1.

## [v0.4] - 2021-09-06

Stuart moves to Python 3, and the Docker image to Alpine Linux and
PostgreSQL.

### Added

- The lint and test tooling is version-pinned — `package.json` and
  `package-lock.json` for `markdownlint-cli`, `csslint` and `dockerlint`,
  and `install-other-deps.sh` for the rest — so a contributor's checks match
  the ones CI runs ([#25](https://github.com/izrik/stuart/pull/25)).

### Changed

- **Python 3.8 replaces Python 2.7**
  ([#24](https://github.com/izrik/stuart/pull/24)). The source was run
  through `2to3` and the shebang updated, so `stuart.py` is run with
  `python3`. It no longer runs under Python 2.

- **The Docker image is built on Alpine Linux**
  (`python:3.8.12-alpine3.14` instead of `python:2.7`), with the compilers
  needed to build the database driver installed and purged inside a single
  layer ([#24](https://github.com/izrik/stuart/pull/24)). The image is
  drastically smaller to pull and store.

- **The image ships a PostgreSQL driver instead of a MySQL one.**
  `psycopg2` replaces `MySQL-python`
  ([#24](https://github.com/izrik/stuart/pull/24)). SQLite still works
  everywhere; a MySQL deployment has to install its own driver or migrate.

- **Dependencies upgraded** and the transitive pins dropped from
  `requirements.txt` ([#24](https://github.com/izrik/stuart/pull/24)): Flask
  0.11.1 to 2.0.1, SQLAlchemy 1.1.4 to 1.4.23, Flask-SQLAlchemy 2.1 to
  2.5.1, Flask-Login 0.4.0 to 0.5.0, Flask-WTF 0.13.1 to 0.15.1, py-gfm
  0.1.0 to 1.0.2, GitPython 2.1.1 to 3.1.18, python-slugify 1.2.1 to 5.0.2,
  python-dateutil 2.6.0 to 2.8.2, and Gunicorn 19.8.1 to 20.1.0 in the
  image. Flask-Cache and Flask-Principal, which were listed but unused, are
  gone.

### Fixed

- **The Docker image reports the version it actually is.** The
  `STUART_VERSION` build variable, and the image label built from it, had
  read `0.1` since the first release and so was wrong for v0.2 and v0.3
  ([#24](https://github.com/izrik/stuart/pull/24),
  [#25](https://github.com/izrik/stuart/pull/25)).

- **Stuart starts when GitPython is not importable**
  ([#25](https://github.com/izrik/stuart/pull/25)). `git` was imported at
  module scope, so an environment without the package failed before serving
  anything. It is now optional, and the footer reports the revision as
  `unknown` when it is absent or when the code is not in a git checkout.

## [v0.3] - 2018-07-02

### Added

- **The release version in the page footer**
  ([#20](https://github.com/izrik/stuart/pull/20)), alongside the git
  revision that was already there, so the version an instance is running can
  be read off any page without shell access to it.

## [v0.2] - 2018-06-29

### Fixed

- **`STUART_PATH_PREFIX` now takes effect under Gunicorn**, which is how the
  Docker image runs ([#19](https://github.com/izrik/stuart/pull/19)). The
  middleware that mounts the app below the prefix was built inside the code
  path that only `python stuart.py` takes, so a containerised wiki served
  every URL from the root and ignored the prefix it was configured with. It
  is now built when the module is imported and exposed as `stuart:gapp`,
  which the container's start script points at.

## [v0.1] - 2018-06-21

First release. Stuart began as a blog engine and this is the wiki it became:
posts are pages, addressed by a slug rather than by date, and the blog's
chronological navigation is replaced by an index of every page and by tag
listings ([#1](https://github.com/izrik/stuart/pull/1),
[#2](https://github.com/izrik/stuart/pull/2),
[#16](https://github.com/izrik/stuart/pull/16)).

### Added

- **A Markdown wiki.** Pages are written in GitHub Flavored Markdown,
  rendered with `py-gfm`, and edited in the browser in a
  bootstrap-markdown editor with a preview tab. A page has a title, an
  automatically generated unique slug that it is addressed by
  (`/page/<slug>`), a summary excerpted from its content for listings, an
  editor-only notes panel, a creation date and a last-updated date that
  moves when the page is edited.

- **An index of every page.** `/all-pages`, linked from the navbar, lists
  all pages sorted by title and paginated
  ([#8](https://github.com/izrik/stuart/pull/8)). A **New Page** link sits
  in the navbar on every page
  ([#10](https://github.com/izrik/stuart/pull/10)).

- **Tags.** A page can carry any number of tags; `/tags` lists the tags that
  have at least one page, with counts, and `/tags/<id>` lists the pages
  carrying one.

- **Private pages**
  ([#12](https://github.com/izrik/stuart/pull/12),
  [#13](https://github.com/izrik/stuart/pull/13),
  [#14](https://github.com/izrik/stuart/pull/14)). A page marked private is
  invisible to anyone not logged in: left out of the listings, uncounted in
  the tag totals, and refused on direct access.

- **A configurable homepage.** Setting the `main_page` option to a page's
  slug shows that page's content at `/` instead of the default index
  ([#11](https://github.com/izrik/stuart/pull/11)).

- **Login.** A bcrypt-hashed password stored in the database is required to
  create or edit a page. `--hash-password PASSWORD` prints the hash to store
  and `--create-secret-key` generates a Flask secret key.

- **Configuration from the environment or the command line**
  ([#16](https://github.com/izrik/stuart/pull/16)): `STUART_SECRET_KEY`,
  `STUART_HOST`, `STUART_PORT`, `STUART_DEBUG`, `STUART_DB_URI`,
  `STUART_SITENAME`, `STUART_PATH_PREFIX`, `STUART_CUSTOM_TEMPLATES`,
  `STUART_AUTHOR` and `STUART_LOCAL_RESOURCES`, each with a matching
  argument that overrides it. Every setting is printed at startup, with the
  database URI and the secret key held back unless `--debug` is on.

- **Running under a URL path prefix.** `--path-prefix` mounts the app below
  a prefix and the templates build their links through it, for serving the
  wiki from a subdirectory behind a reverse proxy
  ([#3](https://github.com/izrik/stuart/pull/3)).

- **Custom templates.** `--custom-templates PATH` adds a directory of Jinja2
  templates that take precedence over the built-in ones, which expose named
  blocks for the purpose. `--local-resources` serves the CSS and JavaScript
  from the app rather than from CDN URLs, for an instance without outbound
  internet access.

- **Admin commands** for a running wiki: `--create-db`,
  `--reset-slug PAGE_ID`, `--reset-summary PAGE_ID`,
  `--set-date PAGE_ID DATE`, `--set-last-updated-date PAGE_ID DATE`, and
  `--set-option NAME VALUE` and `--clear-option NAME` for the settings kept
  in the database. `--list-options [TERM]` prints those settings and their
  values as a table, optionally filtered by name
  ([#5](https://github.com/izrik/stuart/pull/5)).

- **A Docker image** and a Gunicorn start script, so the wiki can be run as
  a container ([#18](https://github.com/izrik/stuart/pull/18)).

- **Site identity.** The configured site name is the navbar brand and part
  of every page title; the footer carries a copyright line naming the
  configured author, a login or logout link, and the git revision the
  running code was built from.

- **A test suite and lint script.** `run_tests.py` covers the page model and
  the setup commands, and `run_tests_with_coverage.sh` runs it under
  coverage followed by flake8, csslint, dockerlint and markdownlint. Both
  run on every push via Travis CI
  ([#17](https://github.com/izrik/stuart/pull/17)).

[Unreleased]: https://github.com/izrik/stuart/compare/v0.7...HEAD
[v0.7]: https://github.com/izrik/stuart/compare/v0.5...v0.7
[v0.5]: https://github.com/izrik/stuart/compare/v0.4...v0.5
[v0.4]: https://github.com/izrik/stuart/compare/v0.3...v0.4
[v0.3]: https://github.com/izrik/stuart/compare/v0.2...v0.3
[v0.2]: https://github.com/izrik/stuart/compare/v0.1...v0.2
[v0.1]: https://github.com/izrik/stuart/releases/tag/v0.1
