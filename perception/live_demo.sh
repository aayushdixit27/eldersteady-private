#!/usr/bin/env bash
# LIVE DEMO — Mac camera -> Modalix board -> terminal reacting. Nothing leaves the room.
# Run on the Mac:   bash perception/live_demo.sh [camera-index] [frames]
# Ctrl-C stops everything.
set -u
CAM="${1:-0}"            # 0 = FaceTime HD, 1 = iPhone (see: ffmpeg -f avfoundation -list_devices true -i "")
FRAMES="${2:-100000}"
BOARD=192.168.1.20
PORT=5004
SDK=ghcr.io-sima-neat-sdk-v2.1.3.0

cleanup() { pkill -P $$ 2>/dev/null; pkill -f "ffmpeg -f avfoundation" 2>/dev/null; pkill -f "ffplay -fflags" 2>/dev/null; }
trap cleanup EXIT INT TERM

# 1. camera -> board (UDP MPEG-TS) and -> local preview (tee)
ffmpeg -hide_banner -loglevel error -f avfoundation -pixel_format uyvy422 -framerate 30 -video_size 1280x720 -i "$CAM" \
  -map 0:v -c:v libx264 -preset ultrafast -tune zerolatency -g 30 -b:v 2M -f tee \
  "[f=mpegts]udp://$BOARD:$PORT?pkt_size=1316|[f=mpegts]udp://127.0.0.1:5005?pkt_size=1316" &
sleep 2
# 2. preview window: what the board sees
( ffplay -fflags nobuffer -flags low_delay -probesize 32 -loglevel error -window_title "what the board sees" -x 640 -y 360 "udp://127.0.0.1:5005" >/dev/null 2>&1 & )
sleep 1
# 3. board runs inference board-local and prints one line per frame; stdout = contract events
TS=$(date -u +%Y-%m-%dT%H:%M:%SZ)
docker exec -u aayushdixit $SDK ssh -t -o BatchMode=yes sima@$BOARD \
  "cd / && source ~/pyneat/bin/activate && python3 /home/sima/watch-perception/watch_events.py \
     --video 'udp://@:$PORT?overrun_nonfatal=1&fifo_size=50000' \
     --model /home/sima/watch-perception/models/yolo26m-det-int8-b1.tar.gz \
     --max-frames $FRAMES --stride 1 --event-after-detections 30 --room living_room --host-ts $TS \
     2>&1 | grep --line-buffered -E '^(frame=|done|\{)' | sed -u -E 's/^frame=([0-9]+) processed=[0-9]+ detections=([0-9]+) best=([0-9.]+) infer_ms=([0-9.]+)/frame \1   people-in-view=\2   confidence=\3   mla=\4ms   uploaded=0/'"
