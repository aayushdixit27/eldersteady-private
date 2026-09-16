# Captures added by the setup lane (round 2)

- `insight-media-sources.jpg` — Insight showing `video01.mp4` as the RTSP media source (H.264, 1280x720, 16 fps).
- `insight-stats.jpg` — Insight live board stats page (CPU / memory / MLA memory / disk).
- `long-run-*.stdout.jsonl` / `.stderr.log` — a 500-frame board-local run
  (`--max-frames 500 --stride 1 --event-after-detections 40`), 8–9 ms/frame on the MLA.
  **Finding:** 500 frames processed, 1 event emitted with `discarded_frames: 40`; the other 460
  processed-and-destroyed frames are not accounted for in any event. Eval item 5 ("exact")
  needs a closing/heartbeat event that carries the remainder.
- Eval item 6 (unmounted `/workspace`) transcript: see `board/findings/lane-setup.md` Addendum 2.
- The Insight **Video Viewer** stays empty: the app sends metadata (UDP 9100) but no video egress
  (UDP 9000). Adding video egress is what would make an "Insight with detections" recording possible.
