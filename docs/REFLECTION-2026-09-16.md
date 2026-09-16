# ElderSteady Private — final reflection, day 2 (16 September 2026, 11:20)

*Written by the setup lane at the founder's request as the board was unplugged. Facts from the repo, the captures and the Senso folder; judgments marked as such.*

## What shipped, measured

- Real falls on camera: by lean (08:03) and by lying on the floor (08:47, and again in test 4 at 10:12 with correct box geometry). Events repeat after a cooldown; timestamps are event time, not session start.
- Pixels-in / bytes-out on the box's own interface: 3.36 MB in, 11 KB out over 150 frames (1:303); long-run 1:98 because the SSH diagnostics were the leak — the counter found its own leak. `cat /sys/class/net/end0/statistics/tx_bytes` is the judge's one-liner.
- Before the fall: sit-to-stand counted on camera; time on the floor; company seconds; a per-minute rhythm record with first-seen and visits; night wandering (clock-shifted demo, labelled `demo_clock`).
- Post-fall voice: offline recogniser on the laptop heard "okay have am okay" in the first live test; "I'm okay" downgrades, "help" escalates, nothing recorded.
- Surfaces: demo.html as a bedside monitor (reference class named in the file), plain-language banner at grade ≤ 3 ("No video leaves this room."), family page on the phone via hotspot, 30-day view (fixture, banner-labelled). Full-screen alert retired at the founder's call.
- Repo public, renamed, README in the founder's order (product thinking → build → box → connections → tools → result); 11 evidence captures; docs/product-findings-log.md and docs/how-we-used-senso.md.

## What the day actually taught

1. **The instrument was wrong for three hours, and the tests said so each time.** Frame-height bands (camera-angle dependent) → box aspect (chair-placement dependent) → thigh drop (body geometry). Under it all, pose boxes were x1y1x2y2, not xywh — every "area", "nearest" and "aspect" before 10:10 was computed on the wrong number. A single `raw_box=` debug field settled it in one look. Rule for next time: **print the raw value before tuning anything on a derived one.**
2. **"Only your shoulders in view — posture paused" was the best classifier change of the day**, because it refuses instead of guessing. Refusal states (close, unclear) are product features, not gaps.
3. **The counter is the product's honesty engine.** It exposed the SSH leak, it made "bytes out" a ceiling claim instead of a promise, and it is the one idea that cleared the crucible (9.6). Everything else orbits it.
4. **Naming by connotation beat naming by cleverness.** Watch / Vigil / Frameless were rejected for what they evoke; ElderSteady Private was chosen by the founder for who it is for. Judgment, not generation.
5. **Six agents, one folder.** Senso held CURRENT.md (rev 4), PROCESS (rev 5), V1–V4, three research rounds, the copy deck, the objections, the outline — 22 documents. Hand-offs went by node id. One false rubric from another hackathon's documents was caught because sources came with ids. Cold start for a fresh lane: ~3.5k tokens.
6. **Review with no stake caught what building could not.** The Opus reviewer found the schema conflict, the frame-line break, the couch-fall bug and det_ms reset in one pass; lane 2 caught three UI defects only by rendering and looking.
7. **Compression was right and I resisted it.** The founder's "change your view of what is possible by 11:30" was correct: with three coding agents and a research lane, the reframe (numbers before the fall), wander, voice, rhythm, det+pose and the redesign all landed in a morning. My timeline management was the wrong instinct; the founder's cadence — 30-minute builds, then "can we demo this?" — was the right one.

## What is still guessed or unverified

Posture thresholds are one room, one camera (now body-geometry based, so more portable — unverified elsewhere). The det+pose second model is merged and reviewed but never ran on the board. Gait cadence never triggered (walks too short). No older adult has seen the banner; no family has received an alert. Audio runs on the laptop, not the MLA. The 30-day series is invented and labelled.

## Cost

Codex: ~2.3 M tokens across ~25 lane runs today (≈ $7 at blended rates; ≈ $190 of $200 remain). Claude: this session plus three Claude Code lanes; one Opus reviewer (67k tokens). GPT-6 research lane: three rounds.

## If there were a day 3

Run the det+pose build once on the box; a 4-second walk for cadence; move audio to the MLA; show an older adult the banner and write down what she says; one real family alert. Then the facility waiver conversation, with the ledger as the evidence.
