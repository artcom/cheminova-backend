#!/usr/bin/env bash

set -eo pipefail

if [[ $(git status --short) != '' ]]; then
  echo 'Git working directory not clean. Please commit or stash your changes before running this script.'
  exit 1
fi

uv version --bump "$1"
uv lock
git add pyproject.toml uv.lock
git commit -m "$(uv version --short)"
git tag -a "v$(uv version --short)" -m "$(uv version --short)"
