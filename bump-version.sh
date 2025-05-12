#!/usr/bin/env bash

set -eo pipefail

uv version --bump "$1"
uv lock
git add pyproject.toml uv.lock
git commit -m "Bump version to $(uv version)"
git tag -a "v$(uv version)" -m "$(uv version)"
