# Perception Demo Runbook

This is the lane-1 demo path for the real Modalix perception run. It uses the
board-local install at `/home/sima/watch-perception`, not files served from the
Mac over `/workspace`.

## What The Demo Proves

- Real YOLO26 detection inference runs through `pyneat` on the Modalix board.
- The app emits contract-shaped `watch.event` JSONL.
- `discarded_frames` is measured in-process by this app: frames pulled from the
  source since the previous event, then destroyed at the application boundary.
- The board-local command can run without `/workspace`; setup lane proved the
  unmounted `/workspace` run in `/workspace/watch-lanes/board/findings/lane-setup.md`
  Addendum 2.

Measurement boundary, for narration:

> We count every frame our application pulled in and destroyed. We do not
> instrument the silicon. The number is exact at the application boundary, which
> is the boundary that decides whether a frame could ever leave the house.

## Capture Evidence

Round-2 item 3 evidence from a real board-local run is in:

- `perception/captures/frame-count-20260916T005534Z.stdout.jsonl`
- `perception/captures/frame-count-20260916T005534Z.stderr.log`
- `perception/captures/frame-count-20260916T005534Z.png`

The event emitted in that run was:

```json
{"type":"wander","room":"living_room","ts":"2026-09-16T00:55:34Z","confidence":0.5,"discarded_frames":1}
```

The same run logged `processed=1` through `processed=12`, showing the app's
frame counter advancing while inference ran.

## Install While The Mac Link Exists

Run from this worktree in the SDK container:

```bash
perception/install_board_local.sh
```

This copies the app, the precompiled YOLO26 detection archive, and the test
video into `/home/sima/watch-perception` on the board.

## Run From Board-Local Storage

With the Mac link connected, this is the repeatable remote command:

```bash
HOST_TS="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
ssh sima@192.168.1.20 \
  "cd / && /home/sima/watch-perception/run_board_local.sh \
    --max-frames 12 \
    --stride 16 \
    --room living_room \
    --host-ts ${HOST_TS}"
```

For the live disconnected demo, start from a board shell or serial console and
run the same board-local command directly:

```bash
cd /
/home/sima/watch-perception/run_board_local.sh \
  --max-frames 12 \
  --stride 16 \
  --room living_room \
  --host-ts 2026-09-16T00:45:55Z
```

Do not use `dk` for the disconnected proof. `dk` depends on the Mac-to-board
link; the point of the demo is that the application path does not.

Setup lane already proved the hard offline case after `umount -l /workspace`:

```bash
cd /
/home/sima/watch-perception/run_board_local.sh \
  --max-frames 4 \
  --stride 16 \
  --room living_room \
  --host-ts 2026-09-16T00:45:55Z
```

That run exited 0 and emitted:

```json
{"type":"wander","room":"living_room","ts":"2026-09-16T00:45:55Z","confidence":0.5,"discarded_frames":1}
```

## Validation

Strip only transport prefixes if the run was launched through `dk`; direct
board execution and `ssh` execution emit plain JSONL on stdout:

```bash
python3 perception/validate_events.py \
  < perception/captures/frame-count-20260916T005534Z.stdout.jsonl
```

## Semantics

The emitted `wander` label is a heuristic over real object detections in a
highway smoke-test video. It is not a fall classifier, a stove classifier, or a
production wandering classifier. The real claims are board inference,
application-boundary frame counting, board-local install, and the offline run.
