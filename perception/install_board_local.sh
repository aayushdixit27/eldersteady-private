#!/usr/bin/env bash
set -euo pipefail

TARGET="${TARGET:-sima@192.168.1.20}"
INSTALL_DIR="${INSTALL_DIR:-/home/sima/watch-perception}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODEL="${MODEL:-/workspace/models/yolo26m-det-int8-b1.tar.gz}"
POSE_MODEL="${POSE_MODEL:-/workspace/models/yolo26m-pose-int8-b1.tar.gz}"
VIDEO="${VIDEO:-/workspace/assets/videos/video01.mp4}"

ssh "${TARGET}" "mkdir -p '${INSTALL_DIR}/models' '${INSTALL_DIR}/videos'"
scp "${ROOT}/watch_events.py" "${ROOT}/run_board_local.sh" "${TARGET}:${INSTALL_DIR}/"
scp "${MODEL}" "${TARGET}:${INSTALL_DIR}/models/"
scp "${POSE_MODEL}" "${TARGET}:${INSTALL_DIR}/models/"
scp "${VIDEO}" "${TARGET}:${INSTALL_DIR}/videos/"
ssh "${TARGET}" "chmod +x '${INSTALL_DIR}/watch_events.py' '${INSTALL_DIR}/run_board_local.sh'"
ssh "${TARGET}" "cd / && '${INSTALL_DIR}/run_board_local.sh' --help >/dev/null"
printf 'installed %s on %s\n' "${INSTALL_DIR}" "${TARGET}"
