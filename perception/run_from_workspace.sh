#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${HOME}/pyneat/bin/activate"
exec python3 "${ROOT}/watch_events.py" "$@"
