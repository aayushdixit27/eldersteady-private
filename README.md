# Watch

California will not let a facility put a camera in her room; at home the same question is yours — this is a fall alert that answers it in bytes.

![Family page flipping red](interface/screenshots/red-flip.png)

### Run it in 3 commands

```sh
POSE=1 bash perception/live_demo.sh
python3 -m http.server 7311 --bind 127.0.0.1
open http://127.0.0.1:7311/interface/demo.html
```

## What it does

- Detects a fall on the MLA in the room.
- Tells the family, not 911.
- Proves in bytes that no frame left: the counter compares video received with every byte transmitted by the board.

## Proof

| Claim | Value | Provenance | Evidence |
|---|---|---|---|
| First real fall | `2026-09-16T15:03:01Z`; lean `63%`; streak `58` frames; confidence `0.916`; `157` frames discarded | measured | [`2026-09-16-0803-first-real-fall.txt`](evidence/captures/2026-09-16-0803-first-real-fall.txt) |
| MLA inference | `8.1–8.3 ms/frame` | measured | [same first-fall capture](evidence/captures/2026-09-16-0803-first-real-fall.txt) |
| Quiet-mode ledger | `150` frames → `3.25 MB` video in, `10.0 KB` out on `end0`; `1 : 324` | measured | This morning with `--print-every` quiet mode; capture file not yet committed |
| Pre-quiet-mode ledger | `3450` frames → `34 MB` in, `739 KB` out; `1 : 46` | measured | [`2026-09-16-0815-second-fall-with-ledger.txt`](evidence/captures/2026-09-16-0815-second-fall-with-ledger.txt), commit `6d0d4e6` |
| Why the pre-quiet ratio was lower | `tx_bytes` counts all protocols on `end0`, including the SSH session carrying per-frame diagnostic lines; quiet mode (`PRINT_EVERY=5`) removed diagnostics from the wire, not events | explanation interpretation | [`live_demo.sh`](perception/live_demo.sh) and the pre-quiet capture above |
| Decoded pixel bytes | frames × `1280` × `720` × `3` | computed | [`demo.html`](interface/demo.html) ledger calculation |
| Fall trigger | `55%` lean for `8` frames | guessed | [`DEMO.md`](perception/DEMO.md) and [`live_demo.sh`](perception/live_demo.sh) |
| Evidence layer | `6/6` eval | fixture | [`pitch/eval-report.md`](pitch/eval-report.md) |
| Second real fall | `2026-09-16T15:06:29Z`; confidence `0.935`; `100` frames discarded | measured | [`2026-09-16-0815-second-fall-with-ledger.txt`](evidence/captures/2026-09-16-0815-second-fall-with-ledger.txt) |

the counter proves the board leaked nothing; in the demo the camera is the Mac.

## Why on-device is the product, not a setting

The ledger exists because inference runs on the MLA. A cloud camera cannot produce this proof: its bytes out are the video. Watch instead accounts for decoded pixels, board-NIC receive/transmit deltas, emitted events, and frames discarded at the application boundary.

The judge can read the board counter over serial before and after a run:

```sh
cat /sys/class/net/end0/statistics/tx_bytes
```

## Product

**Who:** the adult child of an aging parent. **Job:** know, without watching.

The problem is described by caregivers, not a market-size estimate:

> “My mother was found on the floor of her room at the assisted living this morning. Her ankle was broken and dislocated and they don't know how long she was on the floor.” — [r/dementia · +78 score · June 3, 2026](https://www.reddit.com/r/dementia/comments/1tw5u35/)

> “Last week my grandmother couldn’t get off of the ground, but had no way to get anybody’s attention for help.” — [r/eldercare · +10 score · October 19, 2025](https://www.reddit.com/r/eldercare/comments/1oav1eu/)

> “Fell a few times, lost her cane, and was found hours later.” — [r/Alzheimers · +5 score · April 18, 2025](https://www.reddit.com/r/Alzheimers/comments/1k1u5wm/)

**What we refused:** a confidence percentage on the family screen—manufactured certainty is the false-alarm failure; automatic 911—family keeps context; face identification—identity is not the job.

Dave, SiMa mentor: “Fall detection was one of the first things I thought about in senior centers.” “It’s a selling feature.” He also set the scope: “Don’t try to make the product.”

### The 7-gate checklist

| Gate | State | Evidence |
|---|---|---|
| Gate 0 — declare the bar | passed | “Build to learn” is written here; the prototype is not offered as a deployed service. |
| Gate 1 — diagnose the mechanism | passed | The previously unknown number is the `1 : 324` measured quiet-mode video-in:bytes-out ratio. |
| Gate 2 — name the crux | passed | Crux: make “no frame left” checkable at the NIC, not merely make fall detection run. |
| Gate 3 — generate, then cut | open | Directions were cut, but no candidate graveyard records more killed than kept. |
| Gate 4 — sell test | open | Trust is met by captures and the counter; love, buyer-can-succeed, game plan, and urgency remain open pending buyer discovery and an install trial. |
| Gate 5 — attack the assumption | open | The shakiest assumption is the guessed `55%` threshold; the plan does not survive it being false until calibration is tested. |
| Gate 6 — eval and non-goals first | passed | Contracts and fixture eval preceded the build; a separate lane graded it. Non-goals: automatic 911, face identification, recording, diagnosis, and wandering/stove classification. |
| Gate 7 — render and look | passed | [`demo.html`](interface/demo.html) was rendered and inspected; the resulting surface is camera, gauge, ledger, and red event state. |

## Architecture

```text
Mac camera
  -> ffmpeg / UDP MPEG-TS
  -> Modalix
       OpenCV decode
       -> YOLO26-m INT8 pose via pyneat on MLA
       -> torso lean
       -> fall-event JSON
       -> session ledger + `ledger` stdout line
            (pixel_bytes, end0 rx/tx)
  -> interface/index.html  (family)
  -> interface/demo.html   (demo)
```

The board uses YOLO26-m INT8 detection and pose archives from the SiMa model zoo, including `yolo26m-pose-int8-b1.tar.gz`. No Model Compiler install is required. The board runs a `pyneat` virtual environment; app and models live on its NVMe at `/home/sima/watch-perception/`. It ran with `/workspace` NFS unmounted at `2026-09-15 17:50` (measured; [`day1-summary.md`](day1-summary.md)). See the operator [`runbook`](perception/DEMO.md) and [`launcher`](perception/live_demo.sh).

## Honest gaps + roadmap

- The demo camera is the Mac; a board-attached camera is roadmap.
- A daughter across town needs a relay. Today the [`family page`](interface/index.html) is local: Mac hotspot or the Mac itself.
- Calibration is an install step—“show it a fall”—parked at idea-loop `8.3` (fixture reference), unvalidated.
- A facility sale is waiver-gated. CDSS PIN 15-RM-01 says cameras in resident rooms require a Licensing waiver; it provides no analytics-only exemption.
- The `55%` threshold is guessed and unvalidated.

Demo narration and fallbacks: [`demo script`](pitch/demo-script.md), [`video script`](pitch/video-script.md), and [`fixture-only backup`](pitch/backup/index.html).

Built with parallel Claude Code lanes (parallax), with Codex doing code and prose; Senso carried shared memory across sessions. About `$4` of the `$200` Codex budget was spent (guessed).
