# Configuration

Stuart can be configured via environment variables or command-line arguments. CLI arguments take precedence over environment variables.

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `STUART_SECRET_KEY` | `secret` | Flask secret key for sessions and CSRF. **Set this in production.** |
| `STUART_HOST` | `127.0.0.1` | IP address to bind to. Use `0.0.0.0` to accept external connections. |
| `STUART_PORT` | `2512` | Port to listen on. |
| `STUART_DEBUG` | `False` | Enable Flask debug mode (auto-reload, detailed errors). |
| `STUART_DB_URI` | (none) | SQLAlchemy database URI (e.g., `sqlite:///wiki.db`, `postgresql://...`). |
| `STUART_DB_URI_FILE` | (none) | Path to a file containing the database URI (alternative to `STUART_DB_URI`). |
| `STUART_SITENAME` | `Site Name` | Wiki title shown in the navbar and page titles. |
| `STUART_PATH_PREFIX` | (empty) | URL path prefix for running behind a reverse proxy. |
| `STUART_CUSTOM_TEMPLATES` | (none) | Path to a directory with custom Jinja2 templates (overrides built-in templates). |
| `STUART_AUTHOR` | `The Author` | Author name shown in the footer copyright. |
| `STUART_LOCAL_RESOURCES` | `False` | Serve CSS/JS from the app instead of CDN URLs. |

## Command-Line Arguments

```bash
python stuart.py [options]
```

**Server options:**
- `--secret-key KEY` — Flask secret key
- `--host HOST` — IP to bind to
- `--port PORT` — Port to listen on
- `--debug` — Enable debug mode
- `--db-uri URI` — Database connection string
- `--db-uri-file PATH` — File containing database URI
- `--sitename NAME` — Wiki title
- `--path-prefix PREFIX` — URL path prefix
- `--custom-templates PATH` — Custom templates directory
- `--author NAME` — Footer copyright author
- `--local-resources` — Use local CSS/JS

**Admin commands:**
- `--create-db` — Initialize database tables and create default `root` user
- `--create-secret-key` — Generate a random secret key
- `--hash-password PASSWORD` — Print bcrypt hash of a password
- `--create-user EMAIL PASSWORD` — Create a new user account
- `--reset-slug PAGE_ID` — Regenerate slug from title
- `--set-date PAGE_ID DATE` — Set page creation date
- `--set-last-updated-date PAGE_ID DATE` — Set page last-updated date
- `--reset-summary PAGE_ID` — Regenerate page summary from content
- `--list-options [TERM]` — List stored options (optionally filter by name)
- `--set-option NAME VALUE` — Set an option value
- `--clear-option NAME` — Delete an option

## Docker Configuration

In the Docker image, the defaults differ:
- `STUART_PORT=8080`
- `STUART_HOST=0.0.0.0`

The container exposes port 8080 and runs via `docker_start.sh` using Gunicorn.

## Database Options

Setting `main_page` via `--set-option main_page "Page Title"` configures which page content displays on the homepage.
