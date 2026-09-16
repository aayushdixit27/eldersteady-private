# ElderSteady Private — product findings log

*Written 16 September 2026, 10:50, by the setup lane. This is the product thinking, as it actually ran, against the 7-gate procedure in `product_findings_updated_sept14.md`. Rule 1 of that file: most of it will not apply and saying so is the job. Rule 3: say what was not checked. Both applied below.*

## The problem, in one sentence

An adult child wants to know their aging parent is all right, without watching them — and every camera product makes them watch, or asks them to trust a company they cannot check.

## Gate 0 — the bar

**Build to learn.** Declared on day 1 and held: every number is labelled measured / computed / fixture / guessed; nothing is presented as production. The one exception treated as build-to-earn: the ledger arithmetic must close, because it is the claim.

## Gate 1 — the mechanism, with a number nobody had

The number: **3.36 MB of video in, 11 KB out** on the board's own network interface over 150 frames (1 : 303), measured at `/sys/class/net/end0/statistics`. Long-run it was 1 : 98, because the SSH session carrying diagnostics was the leak — the counter found its own leak within an hour of existing, and the fix (`--print-every 5`) came from it. That is the whole argument for measuring instead of asserting.

## Gate 2 — the crux

Not the fall. **A fall product only speaks after the fall, and cries wolf before it.** Cagan's two whys: why it matters (falls) is written everywhere; why families *leave* is the false alarm and the silence until the worst day. The reframe on day 2 — "the numbers before the fall" (sit-to-stand time, time on the floor, company minutes, rhythm) — came from naming this, not from a feature list.

## Gate 3 — generate wide, cut hard: the graveyard

Three crucible rounds (V1→V4, in Senso). **Killed or parked, with reasons:**
- The Unplug (6.0) — the demo camera rides the cable you would pull.
- Facility buyer (7.0) — confirmed rule: CDSS PIN 15-RM-01 needs a Licensing waiver for a camera in a resident's room; a waiver-gated sale is not a hackathon build. Survives as the pitch's last line.
- Headroom meter "rooms per board" (7.0) — an extrapolation nobody could measure before 11:30.
- Two witnesses (8.6) — an output of the counter, not a peer; folded in.
- Phone on the hotspot (8.9) — good, not killer; built anyway (15 min).
- Calibration-by-one-bend (8.3) — a threshold set from one rep can sit above a real partial fall; parked with a floor.
- On-board VLM — SiMa ships Qwen3-VL-4B via LLiMa, but the reference app streams H.264 out; one roadmap sentence.
- Names: Watch (wristwatch), Vigil (death vigil), Frameless/Unseen/Provably (coined, cold) — ElderSteady Private chosen by the founder for connotation.
**Kept:** pixels-in/bytes-out (9.6, the only idea to clear the gate); the reframe; nearest-person subject selection; coverage gate ("only your shoulders in view — posture paused"); post-fall voice ("I'm okay" downgrades the alert).

## Gate 4 — the sell test (Sapp's five)

1. Love the product — specific: it proves, in bytes, that no video left. Met.
2. Trust the seller — a judge can run `cat /sys/class/net/end0/statistics/tx_bytes` over serial and compare with the screen. Met.
3. *They* can get the result — the resident says "I'm okay" and the alert stands down; the daughter reads one banner at grade 3. **Partly met**: no real family has used it.
4. A clear game plan — day 1 baseline, day 30 first trend (the 30-day view is fixture and says so). **Partly met**: the first-30-days is a design, not a run.
5. True urgency — the cost of not acting is the long lie after a fall nobody saw. Met in the argument, not tested on a buyer.
Gaps 3 and 4 are remaining work, not presentation problems.

## Gate 5 — the shakiest assumption

Ranked by fragility: (1) that 2D pose from one camera separates standing / sitting / floor in a real room — **attacked four times on camera today**; the first three classifiers failed (frame-height bands, then a box-format bug: pose boxes are x1y1x2y2, not xywh — every "aspect ratio" before 10:10 was x2/y2). Test 4 passed stand / chair / sit-to-stand / floor / fall with real geometry. (2) That thresholds transfer to another room — **not checked**; calibrated to one camera at 2 m and labelled so. (3) That a family trusts a counter — not checked.

## Gate 6 — eval and non-goals before building

Eval: `evidence/` grader, 6/6 on the fixture; `perception/test_ledger.py` 10+ checks; four controlled on-camera tests with captured logs in `evidence/captures/`. Non-goals held all day: no confidence percentage on the family screen, no face ID, no 911, no cloud inference, no Model Compiler, no Vercel.

## Gate 7 — render it and look

Every UI change was rendered in Chrome and looked at by a person before merge (lanes 2 and 5, and the founder). Three defects were caught only by looking: the page cropped the camera to a face; the red flash re-fired every poll with two events in the log; "Waiting for the board" while 1,515 frames flowed.

## What was considered and did nothing

Doshi's LNO (everything today was leverage or cut); Torres's opportunity tree (one outcome, no tree needed); the AI-productivity-paradox framing (relevant to the retro, not the build); evals-as-PRD beyond the grader (no varying-output AI feature in the product).

## Not checked

No older adult has seen the banner. No family has received an alert. Thresholds are one room, one camera. Audio runs on the laptop, not the box. The 30-day series is invented and labelled.
