#!/usr/bin/env bash
set -euo pipefail

ROOT="${WATCH_PERCEPTION_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)}"
source "${HOME}/pyneat/bin/activate"
if [[ "${POSE:-0}" == "1" ]]; then
  MODEL="${ROOT}/models/yolo26m-pose-int8-b1.tar.gz"
  POSE_ARGS=(--pose)
else
  MODEL="${ROOT}/models/yolo26m-det-int8-b1.tar.gz"
  POSE_ARGS=()
fi
exec python3 "${ROOT}/watch_events.py" \
  "${POSE_ARGS[@]}" \
  --model "${MODEL}" \
  --video "${ROOT}/videos/video01.mp4" \
  "$@"
