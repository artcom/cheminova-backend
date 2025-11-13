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
- [Running Tests](#running-tests)
- [Deployment](#deployment)

---

## Prerequisites

- **[uv](https://docs.astral.sh/uv/getting-started/installation/)**
- **Docker & Docker Compose** (for containerized workflows)

### Running scripts with `uv` and `invoke`

Scripts are defined in `tasks.py` and can be run with `uv`:

```bash
uv run invoke <task-name>
```

List available tasks:

```bash
uv run invoke --list
```

Available tasks:

- bump: Bump version using uv version and create a git tag.
- dev: Run the development server with docker compose.
- export-dump: Dump database and export dump to S3.
- format: Format code using ruff.
- import-dump: Import dump from S3 and load it into the database.
- sync-assets: Sync static and media assets from S3 to local storage.
- test: Run tests using django test framework.

---

## Installation

Clone the repo:

`git clone ***REMOVED***
cd cheminova-backend`

## Local Development (Docker Compose)

- Confugure environment variables

```bash
cp .env.example .env
```

and edit `.env` to set variables as needed.

- Configure the Minio client

```bash
cp config/mc/config.json.example config/mc/config.json
```

and edit it to set access key and secret key for the different environments.

- Bring up the full stack (Postgres, Wagtail, Nginx, Minio)

```bash
uv run invoke dev
```

- Wagtail runs at <http://localhost:8000/>
- Nginx proxy at <http://localhost:8080/>

- Apply database migrations

```bash
docker compose exec wagtail uv run manage.py migrate
```

- Create a superuser

```bash
docker compose exec wagtail uv run manage.py createsuperuser
```

- Create a default site

- Import site data from dev.***REMOVED*** (optional)

```bash
uv run invoke import-dump dev-cheminova <latest-dump-filename>
```

## Running Tests

```bash
uv run invoke test
```

## Deployment

1. Build and push Docker images in GitLab CI (see [.gitlab-ci.yml](.gitlab-ci.yml)).

2. In production, ensure the following env vars are set:
   • SECRET_KEY
   • POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST
   • (Optional) BASE_PATH if serving under a subpath

3. The [production.py](cheminova/settings/production.py) settings module will configure:
   • Secure proxy headers
   • CSRF trusted origins
   • Wagtail admin base URL

## Dump Database and Backup to S3

```bash
docker compose exec wagtail uv run manage.py export_dump
```

## Restore Database

Choose a dump file in the S3 bucket (e.g. [dev-cheminova/db-dump](https://***REMOVED***) for dumps from dev.***REMOVED***). To restore the database from a dump file, you can use the following command:

```bash
docker compose exec wagtail uv run manage.py import_dump $DUMP_FILENAME
```

Users and site data will be restored from the local database unless the `--no-restore-local-data` flag is provided.

## Image Upload Flow

```mermaid
sequenceDiagram
    participant Client
    participant nginx as nginx:8080
    participant wagtail as Wagtail:8000
    participant upload_view as image_upload.views
    participant serializer as ImageModelSerializer
    participant model as CustomImage Model
    participant db as PostgreSQL
    participant fs as File System

    Client->>nginx: POST /api/upload/<br/>(multipart/form-data with image)
    nginx->>wagtail: proxy_pass to wagtail:8000/api/upload/
    wagtail->>upload_view: upload_image_view(request)

    upload_view->>upload_view: Extract file from request.data
    upload_view->>upload_view: Generate UUID filename<br/>(original-{uuid}.ext)
    upload_view->>serializer: ImageModelSerializer(data={file, title})
    serializer->>serializer: validate()

    alt validation successful
        serializer->>model: CustomImage.objects.create()
        model->>db: INSERT image record
        model->>fs: Save image file to /media/original_images/
        model->>serializer: return created instance
        serializer->>upload_view: return serialized data
        upload_view->>wagtail: Response(data, status=201)
        wagtail->>nginx: HTTP 201 with image data
        nginx->>Client: HTTP 201 with image metadata
    else validation failed
        serializer->>upload_view: return errors
        upload_view->>wagtail: Response(errors, status=400)
        wagtail->>nginx: HTTP 400
        nginx->>Client: HTTP 400 with error details
    end
```

## Image Request Flow (with Authentication)

```mermaid
sequenceDiagram
    participant Client
    participant nginx as nginx:8080
    participant wagtail as Wagtail:8000
    participant auth_view as image_auth.views
    participant model as CustomImage Model
    participant db as PostgreSQL
    participant fs as File System

    Client->>nginx: GET /media/images/some-image.jpg
    nginx->>nginx: auth_request /api/image-auth/

    nginx->>wagtail: GET /api/image-auth/<br/>(internal, X-Original-URI header)
    wagtail->>auth_view: check_permissions(request)

    alt user is authenticated
        auth_view->>wagtail: Response(200, "OK")
        wagtail->>nginx: HTTP 200
        nginx->>fs: serve file from /media/
        fs->>nginx: image file content
        nginx->>Client: HTTP 200 with image
    else user not authenticated
        auth_view->>auth_view: get_image_file(X-Original-URI)
        auth_view->>auth_view: get_image_type(image_path)

        alt image type is "rendition"
            auth_view->>model: RenditionModel.objects.get(file=path)
            model->>db: SELECT rendition
            db->>model: rendition record
            model->>auth_view: rendition.image
        else image type is "original"
            auth_view->>model: CustomImage.objects.get(file=path)
            model->>db: SELECT image
            db->>model: image record
            model->>auth_view: image
        end

        auth_view->>model: image.get_referenced_live_pages()
        model->>db: Query page references
        db->>model: live page references

        alt image has live page references
            model->>auth_view: [live_pages]
            auth_view->>wagtail: Response(200, "OK")
            wagtail->>nginx: HTTP 200
            nginx->>fs: serve file from /media/
            fs->>nginx: image file content
            nginx->>Client: HTTP 200 with image
        else no live page references
            model->>auth_view: []
            auth_view->>wagtail: Response(401, "Unauthorized")
            wagtail->>nginx: HTTP 401
            nginx->>Client: HTTP 401 Unauthorized
        end
    end
```

## Image API Request Flow (Metadata)

```mermaid
sequenceDiagram
    participant Client
    participant nginx as nginx:8080
    participant wagtail as Wagtail:8000
    participant api_view as custom_images.views
    participant serializer as CustomImageModelSerializer
    participant model as CustomImage Model
    participant db as PostgreSQL

    Client->>nginx: GET /api/images/<br/>(with Authorization header)
    nginx->>wagtail: proxy_pass to wagtail:8000/api/images/
    wagtail->>api_view: CustomImageViewSet.list(request)

    api_view->>api_view: Check IsAuthenticated permission

    alt user is authenticated
        api_view->>model: CustomImage.objects.all()
        model->>db: SELECT * FROM custom_images
        db->>model: image records

        loop for each image
            model->>serializer: CustomImageModelSerializer(image)
            serializer->>model: get_referenced_live_pages()
            model->>db: Query page references
            db->>model: live page references
            model->>serializer: live pages list
            serializer->>serializer: set 'live' field (len > 0)
            serializer->>api_view: serialized image data
        end

        api_view->>wagtail: Response with image list
        wagtail->>nginx: HTTP 200 with JSON
        nginx->>Client: HTTP 200 with image metadata
    else user not authenticated
        api_view->>wagtail: Response(401, "Unauthorized")
        wagtail->>nginx: HTTP 401
        nginx->>Client: HTTP 401 Unauthorized
    end
```
