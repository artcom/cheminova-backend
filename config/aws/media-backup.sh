#!/bin/bash
# Continuously mirror the media volume to S3. The AWS CLI has no equivalent of
# `mc mirror --watch`, so sync on an interval instead.
set -euo pipefail

while true; do
  aws s3 sync /media "s3://${BUCKET_NAME}/${MEDIA_PREFIX}" --delete --only-show-errors
  sleep "${BACKUP_INTERVAL:-30}"
done
