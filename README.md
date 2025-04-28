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

`uv venv`

By default this creates & manages a .venv directory. ￼

3. Install Python dependencies

`uv pip install -r requirements.txt`

4. Apply database migrations

`uv run python manage.py migrate`

5. Create a superuser

`uv run python manage.py createsuperuser`

6. Collect static files

`uv run python manage.py collectstatic --noinput`

## Local Development

Start the development server (with auto-reload):

`uv run python manage.py runserver 0.0.0.0:8000`

    •	Admin UI: http://localhost:8000/admin/
    •	Wagtail pages: http://localhost:8000/

## Running Tests

`uv run python manage.py test`

## Docker Compose

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
