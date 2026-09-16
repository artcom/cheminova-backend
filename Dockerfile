# syntax=docker/dockerfile:1

ARG DEBIAN_TAG=trixie-slim
ARG PG_MAJOR=18
# The uv-managed CPython must live at the same absolute path in both stages:
# /app/.venv/bin/python and pyvenv.cfg reference it absolutely.
ARG UV_PYTHON_INSTALL_DIR=/opt/uv-python

FROM ghcr.io/astral-sh/uv:0.12.15 AS uv


FROM debian:${DEBIAN_TAG} AS builder

ARG DJANGO_SETTINGS_MODULE="cheminova.settings.production"
ARG ARCH=""
ARG TARGETARCH
ARG UV_PYTHON_INSTALL_DIR

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE \
    UV_PYTHON_INSTALL_DIR=$UV_PYTHON_INSTALL_DIR \
    UV_PROJECT_ENVIRONMENT=/app/.venv \
    UV_CACHE_DIR=/root/.cache/uv \
    UV_LINK_MODE=copy

COPY --from=uv /uv /uvx /usr/local/bin/

# Every dependency in uv.lock currently resolves to a prebuilt wheel, so nothing
# is compiled here; the toolchain is insurance for a future sdist-only
# dependency and costs nothing in the final image.
RUN apt-get update --yes --quiet && apt-get install --yes --quiet --no-install-recommends \
    build-essential \
    libpq-dev \
    libjpeg62-turbo-dev \
    zlib1g-dev \
    libwebp-dev \
    curl \
    unzip \
    ca-certificates \
    postgresql-common \
    && rm -rf /var/lib/apt/lists/*

# Writes /etc/apt/sources.list.d/pgdg.sources and the signing key under
# /usr/share/postgresql-common/pgdg/; both are copied into the final stage.
RUN /usr/share/postgresql-common/pgdg/apt.postgresql.org.sh -y

# The AWS CLI bundles its own Python and CA bundle; at runtime it needs only
# glibc and libz.
RUN case "${ARCH:-$TARGETARCH}" in \
    amd64) AWS_ARCH=x86_64 ;; \
    arm64) AWS_ARCH=aarch64 ;; \
    *) echo "unsupported ARCH: ${ARCH:-$TARGETARCH}" >&2; exit 1 ;; \
    esac \
    && curl --fail --silent --show-error --location "https://awscli.amazonaws.com/awscli-exe-linux-${AWS_ARCH}.zip" -o /tmp/awscliv2.zip \
    && unzip -q /tmp/awscliv2.zip -d /tmp \
    && /tmp/aws/install --install-dir /usr/local/aws-cli --bin-dir /usr/local/bin \
    && rm -rf /tmp/awscliv2.zip /tmp/aws

WORKDIR /app

COPY .python-version .
RUN uv python install

# cheminova-backend is a virtual uv project (no [build-system]), so uv installs
# only the dependencies and needs nothing but pyproject.toml and uv.lock. The
# dev group stays: compose builds with cheminova.settings.dev, which puts
# corsheaders in INSTALLED_APPS.
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --compile-bytecode

COPY ./src .
RUN mkdir -p cheminova/static \
    && uv run --no-sync manage.py collectstatic --noinput --clear


# The runtime stage must stay last: nothing sets a build target.
FROM debian:${DEBIAN_TAG}

ARG DJANGO_SETTINGS_MODULE="cheminova.settings.production"
ARG PG_MAJOR
ARG UV_PYTHON_INSTALL_DIR

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PORT=8000 \
    DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE \
    VIRTUAL_ENV=/app/.venv \
    PATH=/app/.venv/bin:$PATH \
    UV_PYTHON_INSTALL_DIR=$UV_PYTHON_INSTALL_DIR \
    UV_PROJECT_ENVIRONMENT=/app/.venv \
    UV_NO_SYNC=1

# Needed before the pgdg repo is added, because that one is served over HTTPS.
# Also what boto3 and any other outbound HTTPS from Django rely on.
RUN apt-get update --yes --quiet && apt-get install --yes --quiet --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Only the repo definition and the signing key cross the stage boundary, so the
# pgdg bootstrap machinery stays in the builder.
COPY --from=builder /etc/apt/sources.list.d/pgdg.sources /etc/apt/sources.list.d/pgdg.sources
COPY --from=builder /usr/share/postgresql-common/pgdg/apt.postgresql.org.gpg \
                    /usr/share/postgresql-common/pgdg/apt.postgresql.org.asc \
                    /usr/share/postgresql-common/pgdg/

# pg_dump and pg_restore are used by the export_dump and import_dump commands.
RUN apt-get update --yes --quiet && apt-get install --yes --quiet --no-install-recommends \
    postgresql-client-${PG_MAJOR} \
    && rm -rf /var/lib/apt/lists/*

# The internal v2/current symlink is absolute and survives the recursive copy;
# the launcher is recreated because COPY can dereference a symlink named as its
# source path.
COPY --from=builder /usr/local/aws-cli /usr/local/aws-cli
RUN ln -s /usr/local/aws-cli/v2/current/bin/aws /usr/local/bin/aws

COPY --from=builder $UV_PYTHON_INSTALL_DIR $UV_PYTHON_INSTALL_DIR
COPY --from=uv /uv /uvx /usr/local/bin/

RUN useradd -m wagtail

WORKDIR /app

COPY --from=builder --chown=wagtail:wagtail /app/.venv /app/.venv
COPY --from=builder --chown=wagtail:wagtail /app/static /app/static
COPY --chown=wagtail:wagtail ./src .
COPY --chown=wagtail:wagtail pyproject.toml .
COPY --chown=wagtail:wagtail uv.lock .
COPY --chown=wagtail:wagtail .python-version .

# /app must be writable by wagtail for `docker compose watch`; media/* seeds the
# wagtail-media volume on first creation.
RUN install -d -o wagtail -g wagtail \
    /app \
    /app/cheminova/static \
    /app/media/images \
    /app/media/original_images \
    /home/wagtail/.aws

USER wagtail

HEALTHCHECK --interval=30s --timeout=30s --start-interval=5s --start-period=10s --retries=3 CMD ["/app/.venv/bin/python", "-c", "import urllib.request; urllib.request.urlopen(urllib.request.Request('http://localhost:8000/health', method='HEAD'))"]

CMD ["uv", "run", "gunicorn", "cheminova.wsgi:application"]

EXPOSE 8000
