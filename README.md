# ElderSteady Private

California will not let a facility put a camera in her room; at home the same question is yours — this is a fall alert that answers it in bytes.

![Family page flipping red](interface/screenshots/red-flip.png)

### Run it in 3 commands

```sh
POSE=1 bash perception/live_demo.sh
python3 -m http.server 7311 --bind 127.0.0.1
open http://127.0.0.1:7311/interface/demo.html
```

## What it does

- Knows the numbers before the fall: sit-to-stand time and count, floor-lie now and total, daily rhythm, company time, clock-shifted night-wander events, and a post-fall offline voice check — posture is computed on the MLA; wander rules are guessed and the voice listener runs on the laptop, records nothing, and is not on the board.
- Detects a fall on the MLA in the room.
- Tells the family, not 911.
- Proves in bytes that no frame left: the counter compares video received with every byte transmitted by the board.

## Proof

| Claim | Value | Provenance | Evidence |
|---|---|---|---|
| First real fall | `2026-09-16T15:03:01Z`; lean `63%`; streak `58` frames; confidence `0.916`; `157` frames discarded | measured | [`2026-09-16-0803-first-real-fall.txt`](evidence/captures/2026-09-16-0803-first-real-fall.txt) |
| MLA inference | `8.1–8.3 ms/frame` | measured | [same first-fall capture](evidence/captures/2026-09-16-0803-first-real-fall.txt) |
| Quiet-mode ledger, frame 150 | `150` frames → `3.36 MB` video in, `11.1 KB` out on `end0`; `1 : 303` | measured | [`2026-09-16-0833-quiet-mode-with-trend.txt`](evidence/captures/2026-09-16-0833-quiet-mode-with-trend.txt), commit `effbd3b` |
| Quiet-mode ledger, full run | `13,350` frames → `124.0 MB` in, `1.26 MB` out; `1 : 98` | measured | same capture, last `ledger` line |
| Why the long run is worse than frame 150 | the posture-change rule prints extra frame lines while the classifier flaps, and those lines cross `end0` in the SSH session; a classifier fix is in flight and the ratio will be re-measured after it lands — the honest long-run number today is about `1 : 100`, not `1 : 300` | explanation | same capture |
| Pre-quiet-mode ledger | `3450` frames → `34 MB` in, `739 KB` out; `1 : 46` | measured | [`2026-09-16-0815-second-fall-with-ledger.txt`](evidence/captures/2026-09-16-0815-second-fall-with-ledger.txt), commit `6d0d4e6` |
| Why the pre-quiet ratio was lower | `tx_bytes` counts all protocols on `end0`, including the SSH session carrying per-frame diagnostic lines; quiet mode (`PRINT_EVERY=5`) removed diagnostics from the wire, not events | explanation interpretation | [`live_demo.sh`](perception/live_demo.sh) and the pre-quiet capture above |
| Decoded pixel bytes | frames × `1280` × `720` × `3` | computed | [`demo.html`](interface/demo.html) ledger calculation |
| Fall trigger | `55%` lean for `8` frames | guessed | [`DEMO.md`](perception/DEMO.md) and [`live_demo.sh`](perception/live_demo.sh) |
| Before-fall trend | posture test 4 read stand, chair, sit-to-stand, floor, and fall correctly; last line: upright `53.8 s`, sitting `6.4 s`, floor `1.9 s`, `sts_n` `1`, company `89.8 s` | measured values; guessed rules | One controlled test with one person, not validation: [`2026-09-16-1012-posture-test-4-xyxy.txt`](evidence/captures/2026-09-16-1012-posture-test-4-xyxy.txt), commit `25005af`. Earlier tests [`0912-posture-test-1`](evidence/captures/2026-09-16-0912-posture-test-1.txt) and [`0918-posture-test-2`](evidence/captures/2026-09-16-0918-posture-test-2.txt) missed chair or floor as sitting. Capture 0833 showed sitting/absent only. |
| Posture test 4 fall | `2026-09-16T17:12:49Z`; confidence `0.916`; `611` frames discarded; reason `floor`; real xyxy geometry with `WATCH_BOX_XYXY=1` default | measured in one controlled test with one person; not validation | same posture-test-4 capture; commits `80eed0a`, `25005af` |
| Subject selection | nearest person by largest bounding box is the subject; other people count as company; near-equal sizes make the subject `unclear` | implemented, measured live | [`watch_events.py`](perception/watch_events.py), commits `c3edda9`, `1d80e67` |
| Posture and company thresholds | sitting: hips below `0.65` with upright torso; floor: hips and shoulders below `0.85` for at least `2 s`; company: at least `2` people | guessed; measured on one person | rules in [`watch_events.py`](perception/watch_events.py); the published `5×` sit-to-stand over `15 s` comparison is an anchor, while ElderSteady Private measures one rep and is unvalidated |
| Night wander | per-minute `day.json`; event after `3` consecutive night minutes standing or alternating standing/absent; `30 min` cooldown; night `23:00–06:00` | demo_clock (clock-shifted demo); rules guessed | [`RHYTHM.md`](evidence/RHYTHM.md), commits `03938b6`, `a05b2a2`; every clock-shifted event carries `"demo_clock": true` |
| Post-fall voice listener | listens for `60 s` after a fall with offline Vosk, prints heard phrases, records nothing | implemented on the laptop; not on the board | [`VOICE.md`](evidence/VOICE.md), commit `e24cd09`; MLA execution is roadmap |
| 30-day view | interface/trend.html (fixture, landing) | fixture | Not board evidence and not described as measured |
| Evidence layer | `6/6` eval | fixture | [`pitch/eval-report.md`](pitch/eval-report.md) |
| Second real fall | `2026-09-16T15:06:29Z`; confidence `0.935`; `100` frames discarded | measured | [`2026-09-16-0815-second-fall-with-ledger.txt`](evidence/captures/2026-09-16-0815-second-fall-with-ledger.txt) |
| Third real fall (quiet mode) | `2026-09-16T15:24:58Z`; confidence `0.935`; `2183` frames discarded; reason `lean` | measured | [`2026-09-16-0833-quiet-mode-with-trend.txt`](evidence/captures/2026-09-16-0833-quiet-mode-with-trend.txt), commit `effbd3b` |

the counter proves the board leaked nothing; in the demo the camera is the Mac.

## Why on-device is the product, not a setting

The ledger exists because inference runs on the MLA. A cloud camera's bytes out are the video. ElderSteady Private accounts for decoded pixels, board-NIC receive/transmit deltas, emitted events, and frames discarded at the application boundary.

A fall alert is table stakes; every camera vendor and the other team on this track has one. ElderSteady Private adds the numbers before the fall: last sit-to-stand seconds and session count, floor-lie seconds now and total, upright/sitting/floor seconds, and seconds with at least two people in view. They are computed on the MLA from keypoints and ride the same ledger and bytes-out counter; only numbers leave. The thresholds are guessed, and interface/trend.html is a 30-day fixture landing from another lane.

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
| Gate 1 — diagnose the mechanism | passed | The previously unknown number is the measured quiet-mode video-in:bytes-out ratio: `1 : 303` at frame 150, `1 : 98` over 13,350 frames. |
| Gate 2 — name the crux | passed | Crux: make “no frame left” checkable at the NIC, not merely make fall detection run. |
| Gate 3 — generate, then cut | open | Directions were cut, but no candidate graveyard records more killed than kept. |
| Gate 4 — sell test | open | Trust is met by captures and the counter; love, buyer-can-succeed, game plan, and urgency remain open pending buyer discovery and an install trial. |
| Gate 5 — attack the assumption | open | The shakiest assumption is guessed posture and fall bands; posture test 4 measured one controlled pass with one person, which is not calibration or validation. |
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
       -> session ledger `trend` key + `trend` stdout line
            (posture, floor-lie, sit-to-stand, rhythm, company)
  -> laptop rhythm process -> per-minute day.json + demo_clock wander event
  -> laptop offline voice listener after fall (nothing recorded; board port is roadmap)
  -> interface/index.html  (family)
  -> interface/demo.html   (demo)
```

The board uses YOLO26-m INT8 detection and pose archives from the SiMa model zoo, including `yolo26m-pose-int8-b1.tar.gz`. No Model Compiler install is required. The board runs a `pyneat` virtual environment; app and models live on its NVMe at `/home/sima/watch-perception/`. It ran with `/workspace` NFS unmounted at `2026-09-15 17:50` (measured; [`day1-summary.md`](day1-summary.md)). See the operator [`runbook`](perception/DEMO.md) and [`launcher`](perception/live_demo.sh).

## Honest gaps + roadmap

- The demo camera is the Mac; a board-attached camera is roadmap.
- A daughter across town needs a relay. Today the [`family page`](interface/index.html) is local: Mac hotspot or the Mac itself.
- Calibration is an install step—“show it a fall”—scored `8.3` in the idea loop and parked; unvalidated.
- A facility sale is waiver-gated. CDSS PIN 15-RM-01 says cameras in resident rooms require a Licensing waiver; it provides no analytics-only exemption.
- The `55%` fall threshold and posture bands are guessed and unvalidated; posture test 4 is one controlled one-person pass, after tests 1–3 missed chair or floor states.
- Trend values are measured on the board from keypoints. Posture test 4 shows all five tested states and one sit-to-stand; the rules remain open work. The 30-day view is a fixture. Night-wander rules are guessed and its demo event is `demo_clock`; the offline post-fall voice listener records nothing, runs on the laptop, and is not on the board.

Demo narration and fallbacks: [`demo script`](pitch/demo-script.md), [`video script`](pitch/video-script.md), and [`fixture-only backup`](pitch/backup/index.html).

Built with parallel Claude Code lanes (parallax), with Codex doing code and prose; Senso carried shared memory across sessions. About `$4` of the `$200` Codex budget was spent (guessed).
