#!/usr/bin/env bash
# Loads the edge Kamailio config in the official image to validate syntax + module wiring.
# Uses podman (this environment) by default; falls back to docker.
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
IMAGE="${KAMAILIO_IMAGE:-ghcr.io/kamailio/kamailio:6.1.3-resolute}"

ENGINE="${CONTAINER_ENGINE:-}"
if [ -z "${ENGINE}" ]; then
  if command -v podman >/dev/null 2>&1; then ENGINE=podman
  elif command -v docker >/dev/null 2>&1; then ENGINE=docker
  else echo "error: need podman or docker on PATH" >&2; exit 1; fi
fi

# --entrypoint kamailio: the image default entrypoint runs a server and ignores args; override it for a pure -c check.
"${ENGINE}" run --rm --entrypoint kamailio \
  -v "${REPO_ROOT}/docs/kamailio/_etc_kamailio:/usr/local/etc/kamailio:ro" \
  "${IMAGE}" \
  -c -f /usr/local/etc/kamailio/kamailio.cfg
