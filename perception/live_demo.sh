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
LIVE="$(cd "$(dirname "$0")/.." && pwd)/interface/live"; mkdir -p "$LIVE"; : > "$LIVE/board.log"   # the Chrome alert page polls this

cleanup() { pkill -P $$ 2>/dev/null; pkill -x ffmpeg 2>/dev/null; pkill -x ffplay 2>/dev/null; docker exec -u aayushdixit $SDK ssh -o BatchMode=yes -o ConnectTimeout=3 sima@$BOARD "pkill -f watch_events.py" 2>/dev/null; }
trap cleanup EXIT INT TERM

pkill -x ffmpeg 2>/dev/null; pkill -x ffplay 2>/dev/null; sleep 1
docker exec -u aayushdixit $SDK ssh -o BatchMode=yes -o ConnectTimeout=3 sima@$BOARD "pkill -f watch_events.py" 2>/dev/null
# 1. camera -> board (UDP MPEG-TS) and -> local preview (tee)
ffmpeg -hide_banner -loglevel error -f avfoundation -pixel_format uyvy422 -framerate 30 -video_size 1280x720 -i "$CAM" \
  -map 0:v -c:v libx264 -preset ultrafast -tune zerolatency -g 30 -b:v 2M -f tee \
  "[f=mpegts]udp://$BOARD:$PORT?pkt_size=1316|[f=mpegts]udp://127.0.0.1:5005?pkt_size=1316" &
FF=$!
sleep 3
kill -0 $FF 2>/dev/null || { echo 'ffmpeg did not start (camera busy or permission denied). Close other apps using the camera and retry.'; exit 1; }
# 2. preview window: what the board sees
( ffplay -fflags nobuffer -flags low_delay -probesize 32 -loglevel error -window_title "what the board sees" -x 640 -y 360 "udp://127.0.0.1:5005" >/dev/null 2>&1 & )
sleep 1
# 3. board runs inference board-local and prints one line per frame; stdout = contract events
TS=$(date -u +%Y-%m-%dT%H:%M:%SZ)
if [[ "${POSE:-0}" == "1" ]]; then
  MODEL=/home/sima/watch-perception/models/yolo26m-pose-int8-b1.tar.gz
  POSE_ARGS="--pose --min-keypoint-visibility ${KP_VIS:-0.15} --fall-lean-threshold ${LEAN:-55} --fall-consecutive-frames ${BENT:-8}"
else
  MODEL=/home/sima/watch-perception/models/yolo26m-det-int8-b1.tar.gz
  POSE_ARGS=
fi
docker exec -u aayushdixit $SDK ssh -t -o BatchMode=yes sima@$BOARD \
  "cd / && source ~/pyneat/bin/activate && WATCH_BOX_XYXY=${BOX_XYXY:-1} WATCH_PRINT_EVERY=${PRINT_EVERY:-5} python3 /home/sima/watch-perception/watch_events.py \
     --video 'udp://@:$PORT?overrun_nonfatal=1&fifo_size=50000' \
     $POSE_ARGS --model $MODEL \
     --max-frames $FRAMES --stride 1 --print-every ${PRINT_EVERY:-5} --event-after-detections 30 --room living_room --host-ts $TS \
     2>&1 | grep --line-buffered -E '^(frame=|ledger |trend |done|\{|error|Error|Traceback|waiting)' | sed -u -E 's/^frame=([0-9]+) processed=[0-9]+ detections=([0-9]+) best=([0-9.]+) infer_ms=([0-9.]+)/frame \1   people-in-view=\2   confidence=\3   mla=\4ms   uploaded=0/; s/^frame=([0-9]+) processed=[0-9]+ posture=([^ ]+) lean=([0-9]+)% poses=([0-9]+) valid_lean=([0-9]+) best=([0-9.]+) bent_streak=([0-9]+) infer_ms=([0-9.]+) view=([^ ]+)/frame \1   posture=\2   lean=\3%   poses=\4   confidence=\6   streak=\7   mla=\8ms   uploaded=0   view=\9/; s/^frame=([0-9]+) processed=[0-9]+ posture=([A-Za-z]+) lean=([0-9]+%) poses=([0-9]+) valid_lean=1 best=[0-9.]+ bent_streak=([0-9]+) infer_ms=([0-9.]+) view=([^ ]+)/frame \1   posture=\2 lean=\3   people-in-view=\4   bent-for=\5   mla=\6ms   uploaded=0   view=\7/; s/^frame=([0-9]+) processed=[0-9]+ posture=[A-Za-z]+ lean=[0-9]+% poses=([0-9]+) valid_lean=0 best=[0-9.]+ bent_streak=[0-9]+ infer_ms=([0-9.]+) view=([^ ]+)/frame \1   posture=--- (torso not fully in view: step back)   people-in-view=\2   mla=\3ms   uploaded=0   view=\4/; s/ det_ms=([0-9.]+)$/   det=\1ms/'" | tee -a "$LIVE/board.log" | awk '
    /^\{/            { printf "\033[41;97m  ALERT SENT TO FAMILY  %s  \033[0m\n", $0; fflush(); next }
    /posture=BENT/   { printf "\033[31m%s\033[0m\n", $0; fflush(); next }
    /^frame /        { n++; if (n % '"${EVERY:-10}"' == 0) { print; fflush() }; next }
    { print; fflush() }'
