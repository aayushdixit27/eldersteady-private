# Watch — Day 1 Summary (15 September 2026)

*SiMa.ai track, AI Infra Summit hackathon. Written by the setup lane at 20:10 PDT, end of day 1. Board stays at the venue; room reopens 8:00 AM; submission 11:30 AM with a ≤5-minute video; live pitches 1–3 PM, room 207.*

## The product, one sentence

A room camera for families with an aging parent: it detects a fall on-device, tells the family (not 911), and can prove that no frame ever left the room — a privacy ledger that counts every frame processed and destroyed.

## What is real, right now, on `main` (`aa05cf3`)

| Piece | State | Provenance |
|---|---|---|
| Live camera → board | Mac FaceTime/iPhone camera → ffmpeg → UDP MPEG-TS → Modalix reads it with OpenCV | measured, works |
| Inference | YOLO26-m INT8 (det or pose) on the MLA, **8–9 ms/frame** | measured |
| Person count | `people-in-view` reacts live (1→2→3 as people walk in) | measured |
| Lean / posture | 17 COCO keypoints → torso lean (shoulders→hips; nose→shoulders fallback at close range) | measured per frame; **55 % threshold / 8-frame window are unvalidated guesses** |
| Fall event | `type=fall` JSON on the contract after N bent frames | code works; **no real bend→fall captured on camera yet** |
| Session ledger | `frames_processed / in_events / unattributed / events / stored=0 / uploaded=0`, arithmetic closes | measured |
| Board-local run | app + models on the board's NVMe; runs with `/workspace` NFS **unmounted** (proven 17:50) | measured |
| Evidence layer | events → incidents, 6/6 eval on the hand-written fixture | fixture |
| Family alert page | `interface/index.html`, contrast-audited, live strip + card flips red on a real event | tested with a simulated log |
| Demo page | `interface/demo.html`: camera left, lean gauge / counters / ledger right, full-screen red on fall | tested with a simulated log |
| README + pitch | rewritten around the above, with the mentor's quotes and provenance labels | prose |

## Timeline

**10:20–11:30 — Host setup.** Colima (not Docker Desktop), `sima-cli` 2.1.17, workspace. Online SDK download stalled; loaded `ghcr.io/sima-neat/sdk:v2.1.3.0` from the mentor USB instead. Model Compiler skipped (27 GB free vs ~20 GB needed).

**11:30–14:30 — Board pairing.** Serial console found via FTDI (`/dev/cu.usbserial-*`; a `usbmodem` device was the Anker hub, not the board). Board `192.168.1.20`, Mac `192.168.1.10` on `en8`. `sima-cli sdk setup --devkit` completed but the DevKit bootstrap failed with `Permission denied (publickey)`.

**14:30–15:00 — Root cause.** `--network-host-addresses` puts the Mac's IP on the Colima VM loopback as **/24**, so the container's SSH to `192.168.1.20` hit the VM's own sshd. Fix: `/24 → /32` on `lo`, install the container key on the board over serial, re-run `devkit.sh`. `dk hello.py` printed from the board. `setup.md` written (local + Senso).

**16:30–17:15 — Parallax round 1.** Architect (a separate Cowork session) wrote MISSION.md, contracts, four briefs. Lanes ran on Codex: lane 1 in the SDK container (board access), lanes 2–4 on the Mac under Codex's sandbox (network blocked = mechanical fence). First launch failed: the prompt "write only to findings" was read literally, so lanes wrote no deliverables. Relaunched with a corrected prompt. Codex's sandbox also blocked commits (`.git/worktrees` outside the writable root) → `--add-dir .git` from round 2.

**17:15–17:50 — Round 1 lands.** Lane 1: real YOLO26 inference on the MLA, one contract event, exact per-event frame count, board-local install. Lanes 2–4: evidence module (5/5 tests), alert page, README/pitch/backup deck. Setup lane proved eval item 6 (NFS unmounted, app still runs). Board unplugged for a meeting; recovered with `nmcli connection up end0-static` over serial.

**17:50–18:30 — Round 2.** Merged all lanes. Setup lane found the ledger gap (500 processed, 40 attributed) → architect ruled `session-ledger.json` instead of a heartbeat event; lane 1 r3 landed it. Lane 4 regraded the merged tree: 6 pass / 0 fail with provenance. Design pass (anti-design-slop skill): 6 of 12 text pairs were under 7:1; fixed, DESIGN.md written.

**18:40–19:10 — The live demo.** First SiMa mentor chat: "not even sending a frame — just the analysis, recording the reasoning rather than the frame." Second (Dave): "person detection is not particularly novel… if you can detect I'm 5 % bent over versus 0 %, you've got your solution… don't try to make the product… fall detection was one of the first things I thought about in senior centers… it's a selling feature." Built `live_demo.sh`: camera → board → terminal reacting. Worked first try (`people-in-view=1 confidence=0.97`).

**19:20–19:50 — Pose.** Lane 1 r4 (Codex, 4 minutes): pose model, keypoint decode, torso lean, fall event. Live test: keypoints real, but hips off-frame at desk distance → added nose→shoulder fallback. A pile of stale `ffmpeg` processes (bad `pkill` pattern) and a stale board process holding the UDP port caused the "error on top of error" stretch; both fixed in the script. Third mentor chat: lean visibly changing; "show me black-and-red when a fall happens"; another team is doing fall detection.

**19:50–20:05 — Demo surface.** Lanes 3 and 4 r3 on Codex (4 minutes each): `demo.html` and the README/pitch rewrite. Terminal output throttled and coloured. Board unplugged for the night.

## Cost

Codex (hackathon key): ~$3 of $200 across ~12 lane runs. The expensive side was the two Claude sessions (architect + setup).

## What Dave and the mentors actually said, for the pitch

- "Not even sending a frame — just the analysis, and recording the reasoning rather than the frame itself."
- "Person detection is not particularly novel." → hence pose.
- "If you can detect I'm 5 % bent over versus 0 % bent over, you know that you've got your solution in front of you."
- "Don't try to make the product." Calibration "could require a month of testing — can be roadmapped."
- "Fall detection was one of the first things I thought about in senior centers." "It's a selling feature."
- "I can't read the numbers on the screen that fast… something black and red."

## Differentiation

Another team on the track is doing fall detection. Ours: the fall is table stakes; the product is the **ledger** — frames processed, destroyed, zero uploaded, family first, no 911 — which only exists because inference happens on the MLA in the room. On a cloud camera the frame has already left before anyone could count it.

## Morning checklist (8:00 AM)

1. Plug in Ethernet adapter (direct, not via hub), UART, power. `dk status` from the container. If unreachable: over serial, `sudo nmcli connection up end0-static`. If Colima restarted: the `/24→/32` fix in `setup.md`.
2. `cd ~/workspace/watch && python3 -m http.server 7311 --bind 127.0.0.1 &`
3. `POSE=1 bash perception/live_demo.sh` — preview window + terminal; open `http://127.0.0.1:7311/interface/demo.html` in Chrome, click Start camera.
4. **Capture one real bend → red ALERT.** Stand 2 m back, whole body in frame, bend, hold 3 s. This is the only unproven beat.
5. Record the 5-minute video: (1) demo page with the fall flip, (2) unplug the Mac's Ethernet, run from serial, ledger still writes, (3) alert page close-up. Rooms 206/207 are quiet.
6. Submit by 11:30 on the LabLab form (README is the judged product page). Sign up for the 1 PM pitch via the QR.

## Known gaps, honestly

- No real fall event captured on camera yet (only simulated logs drove the page's red state).
- Lean threshold and window are guesses; "wander" and "stove" are not implemented — roadmap.
- `demo.html`'s camera pane is the Mac's camera shown locally; the board's view is the same stream, but they are two consumers of one camera, not a round-trip.
- Backup deck (`pitch/backup/`) is dark-with-yellow and was not restyled; fallback only.
- Colima loopback fix and the board's static IP both have to be re-applied by hand after restarts/re-plugs.

## Where everything is

- Repo: `~/workspace/watch` (main), lanes at `~/workspace/watch-lanes/`, board at `~/workspace/watch-lanes/board/`
- Runbook: `setup.md` (Senso: AI Infra Hackathon folder, node `a9d9b89c-…`)
- Demo: `perception/live_demo.sh`, `perception/DEMO.md`, `interface/demo.html`, `interface/index.html`
- Pitch: `README.md`, `pitch/demo-script.md`, `pitch/video-script.md`, `pitch/sell-test.md`, `pitch/eval-report.md`
- Design: `DESIGN.md`
