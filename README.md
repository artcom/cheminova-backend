# Cheminova Backend

Wagtail CMS and API backend for the Cheminova site, providing:

- A single “Home” page with image support
- Secure image upload and per-request authorization
- Custom image model with renditions and live-page tracking
- JSON API endpoints for pages and images
- Containerized development and deployment with Docker & Docker Compose

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Local Development](#local-development)
- [Running Tests](#running-tests)
- [Docker Compose](#docker-compose)
- [Deployment](#deployment)

---

## Prerequisites

- **Python 3.13+**
- **uv** (Python package manager)
- **Docker & Docker Compose** (for containerized workflows)

### Install `uv`

Install `uv` via the standalone installer:

```bash
# macOS & Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

￼

⸻

## Installation

1. Clone the repo

`git clone ***REMOVED***
cd cheminova-backend`

2. Create a virtual environment

```bash
uv python install 3.13
uv venv --python 3.13
```

By default this creates & manages a .venv directory. ￼

3. Install Python dependencies

`uv pip install -r requirements.txt`

4. Apply database migrations

`uv run python manage.py migrate`

5. Create a superuser

`uv run python manage.py createsuperuser`

6. Collect static files

`uv run python manage.py collectstatic --noinput`

## Local Development (Python)

Start the development server (with auto-reload):

`uv run python manage.py runserver 0.0.0.0:8000`

    •	Admin UI: http://localhost:8000/admin/
    •	Wagtail pages: http://localhost:8000/

## Running Tests

`uv run python manage.py test`

## Local Development (Docker Compose)

Bring up the full stack (Postgres, Wagtail, Nginx):

`docker compose up --build`

    •	Wagtail runs at http://localhost:8000/
    •	Nginx proxy at http://localhost:8080/

## Deployment

1. Build and push Docker images in GitLab CI (see .gitlab-ci.yml).

2. In production, ensure the following env vars are set:
   • SECRET_KEY
   • POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST
   • (Optional) BASE_PATH if serving under a subpath

3. The production.py settings module will configure:
   • Secure proxy headers
   • CSRF trusted origins
   • Wagtail admin base URL

## Dump Database

```bash
docker compose exec database /bin/bash -c 'pg_dump -U cheminova -Fc cheminova > /var/lib/postgresql/backup/cheminova.dump'
```

## Backup Database

1. Set up a DigitalOcean Spaces bucket and configure the `s3cmd` tool with your credentials. You can do that by using s3cmd command line tool as described [here](https://docs.digitalocean.com/products/spaces/reference/s3cmd/):

```bash
mkdir -p s3cmd
docker run --rm -it \
  -v $PWD/.s3cfg-2:/root/.s3cfg \
  d3fk/s3cmd:latest \
  --configure
```

2. To back up the database to a DigitalOcean Spaces bucket using the d3fk/s3cmd image, use the following command:

```bash
docker run --rm \
  -v backend_wagtail-db-backup:/cheminova-backup \
  -v $PWD/s3cmd/.s3cfg:/root/.s3cfg \
  d3fk/s3cmd:latest \
  put /cheminova-backup/cheminova.dump s3://cheminova/db-dump/cheminova-$(date +"%Y-%m-%d_%H-%M-%S").dump
```
