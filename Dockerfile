FROM debian:bookworm-slim

ENV PYTHONUNBUFFERED=1
ENV PORT=8000
ARG DJANGO_SETTINGS_MODULE="cheminova.settings.production"
ENV DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE

RUN apt-get update --yes --quiet && apt-get install --yes --quiet --no-install-recommends \
    build-essential \
    libpq-dev \
    libjpeg62-turbo-dev \
    zlib1g-dev \
    libwebp-dev \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*
COPY --from=ghcr.io/astral-sh/uv:0.7.0 /uv /uvx /usr/local/bin/

WORKDIR /app
RUN useradd -m wagtail
RUN chown -R wagtail:wagtail /app
USER wagtail
COPY --chown=wagtail:wagtail ./src .
COPY --chown=wagtail:wagtail pyproject.toml .
COPY --chown=wagtail:wagtail uv.lock .
COPY --chown=wagtail:wagtail .python-version .
RUN mkdir media
RUN mkdir cheminova/static
RUN uv sync --locked --compile-bytecode
RUN uv run manage.py collectstatic --noinput --clear

HEALTHCHECK --interval=30s --timeout=30s --start-interval=5s --start-period=10s --retries=3 CMD ["curl", "--head", "--fail", "http://localhost:8000/health"]

CMD ["uv", "run", "gunicorn", "cheminova.wsgi:application"]

EXPOSE 8000
