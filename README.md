# Stuart

A Python wiki system built on Flask.

<https://github.com/izrik/stuart>

## Quick Start

```bash
# Install dependencies
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt

# Initialize and run
python stuart.py --db-uri "sqlite:///wiki.db" --create-db
```

Open <http://127.0.0.1:2512> in your browser. The default user credentials are printed to the console on first run.

## Features

- Markdown/GFM content with live preview
- User authentication
- Page tagging
- Private pages
- Custom templates
- SQLite or PostgreSQL storage

## Configuration

Stuart is configured via environment variables (`STUART_*`) or command-line arguments. Common options:

| Variable | Default | Description |
|----------|---------|-------------|
| `STUART_HOST` | `127.0.0.1` | IP to bind to |
| `STUART_PORT` | `2512` | Port to listen on |
| `STUART_DB_URI` | (none) | Database URI |
| `STUART_SITENAME` | `Site Name` | Wiki title |

See [docs/configuration.md](docs/configuration.md) for all options.

## Docker

```bash
docker build -t stuart .
docker run -p 8080:8080 -e STUART_DB_URI="sqlite:////data/wiki.db" stuart
```

## License

AGPL-3.0
