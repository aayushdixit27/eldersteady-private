#!/usr/bin/env bash
set -euo pipefail

port="${PORT:-7311}"
ip="${IP:-}"

if [[ -z "$ip" ]]; then
  for interface in bridge100 en0 en1; do
    ip="$(ipconfig getifaddr "$interface" 2>/dev/null || true)"
    [[ -n "$ip" ]] && break
  done
fi

if [[ -z "$ip" ]]; then
  echo "Error: turn on Internet Sharing or join a Wi-Fi network."
  exit 1
fi

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$script_dir/.."
echo "Open on your phone: http://${ip}:${port}/interface/index.html"
exec python3 -m http.server "$port" --bind "$ip"
