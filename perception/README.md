# Perception Lane

This directory contains the round-1 perception event probe. It runs YOLO26 object
detection on the Modalix board through `pyneat`, reads frames from the supplied
test video, and emits one `watch.event` JSON object per line to stdout.

## What Is Real

- Model execution uses the precompiled Model Zoo archive
  `/workspace/models/yolo26m-det-int8-b1.tar.gz`.
- The runtime path is board-side `pyneat` with `TensorMemory.EV74`; no CPU model
  fallback is used by this code.
- `discarded_frames` is an exact in-process count of frames read, sent to the
  model route, and then dropped by this application since the previous event.

## What Is Stubbed

- The emitted `wander` label is a round-1 heuristic over real object detections:
  the first sampled frame with a YOLO26 detection becomes a `wander` event.
- The supplied `/workspace/assets/videos/video01.mp4` is a highway smoke-test
  video, not a home fall/wandering/stove scene.
- The app does not prove a clinical fall detector or a production activity
  classifier. It only tests whether real board inference can produce
  contract-shaped events and exact per-event frame counts.

## Run From Workspace

```bash
dk /workspace/watch-lanes/lane-1/perception/watch_events.py \
  --max-frames 8 \
  --stride 16 \
  --room living_room
```

Only JSONL events are written to the application stdout. `dk` adds its own
transport prefix; strip `[DEVKIT][STDOUT] ` before feeding captured `dk` output
to downstream tools. Direct board execution does not add this prefix.

Validate the JSONL shape:

```bash
dk /workspace/watch-lanes/lane-1/perception/watch_events.py \
  --max-frames 8 \
  --stride 16 \
  > /tmp/watch-events.raw
sed -n 's/^\[DEVKIT\]\[STDOUT\] //p' /tmp/watch-events.raw |
  python3 perception/validate_events.py
```

## Board-Local Install

Install the app, model archive, and video to board-local storage:

```bash
perception/install_board_local.sh
```

Run it without depending on `/workspace` paths:

```bash
ssh sima@192.168.1.20 \
  'cd / && /home/sima/watch-perception/run_board_local.sh --max-frames 8 --stride 16'
```

The command starts from `/`, uses `/home/sima/watch-perception/...` for the
script/model/video, and activates the board-local `~/pyneat` environment.

To send detection metadata to Insight channel 0 while emitting contract JSONL:

```bash
ssh sima@192.168.1.20 \
  'cd / && /home/sima/watch-perception/run_board_local.sh \
    --max-frames 8 --stride 16 \
    --insight-host 192.168.1.10 --insight-metadata-port 9100'
```

This sends real detection metadata to Insight's UDP metadata ingress. The app
does not send synchronized video to the viewer, so this is an ingress check, not
proof of rendered overlays.
