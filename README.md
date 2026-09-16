# Watch

California will not let a facility put a camera in her room; at home the same question is yours — this is a fall alert that answers it in bytes.

CDSS PIN 15-RM-01 requires a Licensing waiver for cameras in resident rooms; it gives no analytics-only exemption. Watch is a family-first fall alert that runs inside the home. A live Mac camera feeds a Modalix MLSoC over UDP; YOLO26 runs on the MLA; sustained body lean turns the family alert page red.

No clip is saved. No frame is uploaded. No call centre watches. Watch tells family first and does not call 911.

> “Fall detection was one of the first things I thought about in senior centers.”
>
> “It’s a selling feature.”
> — Dave, SiMa mentor

## What is real as of this morning

Until this morning, only simulated logs had driven the red state. At **2026-09-16T15:03:01Z (MEASURED; 08:03 PDT)**, a real person bent in front of the live camera and Watch emitted its first real fall event. Lean peaked at **63% (MEASURED)** against a **55% threshold (GUESS)**; the streak reached **58 frames (MEASURED)**, event confidence was **0.916 (MEASURED)**, **157 frames (MEASURED)** were discarded at the application boundary, and MLA time was **8.1–8.3 ms per frame (MEASURED)**.

The pixels-in / bytes-out counter, B′, is also live. `watch_events.py` prints `ledger frames=… pixel_bytes=… rx_bytes=… tx_bytes=… nic=end0`; [`interface/demo.html`](interface/demo.html) shows video in, bytes out, pixels decoded, and their ratio. At **60 frames (MEASURED)** it reported **165.9 MB of decoded pixels (COMPUTED: 60 × 1280 × 720 × 3)**, **2.55 MB video in (MEASURED on `end0`)**, **15.2 KB out (MEASURED on `end0`, all protocols, including the SSH session carrying per-frame diagnostics)**, and **1 : 168 video-in : bytes-out (COMPUTED from measured NIC counters)**. That run also fired a second real fall at **2026-09-16T15:06:29Z (MEASURED)** with **0.935 confidence (MEASURED)** and **100 discarded frames (MEASURED)**.

Quiet mode landed in commit `62a2b44`: `--print-every`, with `PRINT_EVERY=5` in `live_demo.sh`. The **15.2 KB (MEASURED)** value predates quiet mode. Its purpose is to make bytes-out reflect events rather than per-frame diagnostics; the quiet-mode transmit figure is not measured yet and will be read live.

the counter proves the board leaked nothing; in the demo the camera is the Mac.

## The live path we built

**Mac camera → UDP → Modalix → YOLO26 pose → measured lean → possible-fall event → family alert**

YOLO26 pose runs on the Modalix MLA at **8.1–8.3 ms per frame (MEASURED in the first real-fall capture)**. Keypoints produce the torso-lean gauge. A sustained lean crosses the configured **55% threshold (GUESS)** for an **8-frame window (GUESS)**, emits a possible-fall event, and flips the family page red.

This is a prototype trigger, not a medical claim. Lean is measured from model keypoints; the policy is not validated in homes or senior centers. “Wander” in an earlier build was a heuristic, not a validated behavior classifier. Calibration is roadmap, not something we pretend to have finished.

As Dave advised: **“Don’t try to make the product.”** We built the one decisive path and made its limits visible.

## Privacy you can inspect

Privacy is usually a promise. Watch makes it an accounting invariant. The session ledger accounts for `frames_processed`, `frames_in_events`, `frames_unattributed`, `events_emitted`, `frames_stored`, and `frames_uploaded`; the B′ line adds decoded `pixel_bytes` and the `end0` receive/transmit byte deltas:

```text
ledger frames=60 pixel_bytes=165888000 rx_bytes=2550794 tx_bytes=15182 nic=end0
```

For that pre-quiet-mode snapshot: **60 frames (MEASURED)**; **165,888,000 pixel bytes (COMPUTED)**; **2,550,794 receive bytes (MEASURED)**; **15,182 transmit bytes (MEASURED, all protocols including SSH diagnostics)**; and **1 : 168 video-in : bytes-out (COMPUTED)**. The event ledger reports **uploaded 0 (MEASURED at the application boundary)** and **stored 0 (MEASURED at the application boundary)**. The NIC count is the external check; the application ledger says what the app did with frames.

Over serial, the judge can read the board counter directly:

```sh
cat /sys/class/net/end0/statistics/tx_bytes
```

### Claim provenance

| Claim | Value | Provenance (measured/computed/guess/fixture) | Evidence file or command |
|---|---:|---|---|
| First real fall event time | 2026-09-16T15:03:01Z / 08:03 PDT | measured | `evidence/captures/2026-09-16-0803-first-real-fall.txt` |
| First real-fall peak lean | 63% | measured | `evidence/captures/2026-09-16-0803-first-real-fall.txt` |
| Trigger threshold | 55% | guess | `perception/DEMO.md` |
| Trigger window | 8 frames | guess | `perception/DEMO.md` |
| First real-fall streak / confidence / discarded | 58 frames / 0.916 / 157 frames | measured | `evidence/captures/2026-09-16-0803-first-real-fall.txt` |
| First real-fall MLA time | 8.1–8.3 ms per frame | measured | `evidence/captures/2026-09-16-0803-first-real-fall.txt` |
| B′ sample size | 60 frames | measured | `evidence/captures/2026-09-16-0815-second-fall-with-ledger.txt` |
| Decoded pixels at sample | 165.9 MB / 165,888,000 bytes | computed | `60 × 1280 × 720 × 3` |
| Video in / bytes out | 2.55 MB / 15.2 KB | measured | `evidence/captures/2026-09-16-0815-second-fall-with-ledger.txt` |
| Video-in : bytes-out | 1 : 168 | computed | measured `end0` receive/transmit counters above |
| Second real fall event / confidence / discarded | 2026-09-16T15:06:29Z / 0.935 / 100 frames | measured | `evidence/captures/2026-09-16-0815-second-fall-with-ledger.txt` |
| Quiet-mode transmit bytes | not yet measured | measured live during judging | `cat /sys/class/net/end0/statistics/tx_bytes` |
| Backup UI values | explicitly labelled replay values | fixture | `pitch/backup/index.html` |

## Why this wins even against another fall detector

Another team also does fall detection — differentiate on the ledger. Watch accounts for processed pixels and the bytes crossing the board NIC, keeps the response family-first, has no monitoring centre or automatic 911 call, and creates no video archive to browse later.

The product is a different agreement between a parent and their family: know when help may be needed without acquiring surveillance.

## Five-beat demo

1. **Counter.** Open [`interface/demo.html`](interface/demo.html); show video in, bytes out, pixels decoded, and the ratio climbing with their MEASURED / COMPUTED labels.
2. **Bend.** Bend on the real Mac camera and let measured lean cross the **55% threshold (GUESS)**.
3. **Red flip.** Hold through the **8-frame window (GUESS)**; show the fall event and [`interface/index.html`](interface/index.html) turning red.
4. **Ledger.** Show session frames, `pixel_bytes`, NIC receive/transmit bytes, **uploaded 0 (MEASURED)**, and **stored 0 (MEASURED)**; then run the serial one-liner.
5. **Phone.** Open the family page on a phone over the Mac hotspot if it is up; otherwise show the same page on the Mac.

The demo does not establish accuracy, clinical safety, alert-delivery reliability, or validated thresholds.

## Run the live demo

The operator runbook is [`perception/DEMO.md`](perception/DEMO.md). The launcher is [`perception/live_demo.sh`](perception/live_demo.sh); the counter view is [`interface/demo.html`](interface/demo.html); and the family view is [`interface/index.html`](interface/index.html). A clearly labelled fixture-only backup remains in [`pitch/backup/index.html`](pitch/backup/index.html), but it is not hardware evidence.

**Watch — care without surveillance.**
