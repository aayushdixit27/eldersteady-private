#!/usr/bin/env bash
set -euo pipefail

ROOT="${WATCH_PERCEPTION_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)}"
source "${HOME}/pyneat/bin/activate"
exec python3 "${ROOT}/watch_events.py" \
  --model "${ROOT}/models/yolo26m-det-int8-b1.tar.gz" \
  --video "${ROOT}/videos/video01.mp4" \
  "$@"
