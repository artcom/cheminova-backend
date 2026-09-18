#!/bin/sh
set -e

# nginx serves the collected assets from a named volume mounted over /app/static, and Docker
# seeds such a volume from the image only while it is still empty. A new image therefore leaves
# the assets of the old one in place, and every {% static %} of a file added since then raises
# "Missing staticfiles manifest entry". Collecting on every start keeps the volume in step with
# the code in this image.
uv run manage.py collectstatic --noinput

exec "$@"
