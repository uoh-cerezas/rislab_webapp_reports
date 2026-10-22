#!/usr/bin/env bash
set -euo pipefail

# Runtime values live outside Git. This script is intentionally free of
# database, SSH and Flask credentials.
APP_NAME="${APP_NAME:-dashboard_app}"
NETWORK_NAME="${NETWORK_NAME:-FIC-app-network}"
PORT="${PORT:-8050}"
IMAGE="${IMAGE:-dashboard_image}"
ENV_FILE="${DASHBOARD_ENV_FILE:-/home/uoh/cerezas_web_server/config/dashboard.env}"
DATA_ROOT="${CLIMATE_REPORTING_DATA_HOST:-/home/uoh/cerezas_web_server/data/climate-reporting}"
NOC_UPSTREAM_URL="${NOC_UPSTREAM_URL:-http://ttn-noc:8060}"

test -r "$ENV_FILE" || {
  echo "Missing runtime env file: $ENV_FILE" >&2
  exit 1
}
test -d "$DATA_ROOT" || {
  echo "Missing climate-reporting data directory: $DATA_ROOT" >&2
  exit 1
}


docker run -d \
  --name $APP_NAME \
  --network $NETWORK_NAME \
  -p $PORT:8050 \
  --env-file "$ENV_FILE" \
  -e CLIMATE_REPORTING_DATA_ROOT=/data \
  -e NOC_UPSTREAM_URL="$NOC_UPSTREAM_URL" \
  -v "$DATA_ROOT:/data:ro" \
  --restart unless-stopped \
  "$IMAGE"
