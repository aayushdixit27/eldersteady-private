# Live demo — five beats, about 2 minutes

California will not let a facility put a camera in her room; at home the same question is yours — this is a fall alert that answers it in bytes.

Before presenting: open `interface/demo.html`, start the phone page with `interface/serve-phone.sh`, and keep a large terminal running `perception/live_demo.sh`. Confirm pose mode, camera preview, lean gauge, live counter, and serial access. Keep the fixture backup closed unless the live path fails.

## Beat 1 — counter running (0:00–0:25)

**Show:** `demo.html`, with the labels visible while video in, bytes out, pixels decoded, and the ratio climb.

**Say:**

“This is the live accounting surface. Video in and bytes out are MEASURED on the board’s `end0` NIC, all protocols. Pixels decoded are COMPUTED as frames times width times height times three. The ratio is COMPUTED from the measured NIC counters.”

“At 60 frames, this morning’s pre-quiet-mode run showed 165.9 MB COMPUTED pixels, 2.55 MB MEASURED video in, and 15.2 KB MEASURED out: 1 to 168, COMPUTED. The 15.2 KB included SSH per-frame diagnostics; quiet mode has landed, and we’ll read its transmit figure live rather than claim an unmeasured number.”

## Beat 2 — bend on camera (0:25–0:48)

**Show:** Stand upright in the live Mac camera, then bend. Point to real lean and the gauge crossing **55% (GUESS)**.

**Say:**

“The camera is this Mac. It sends video over UDP to Modalix; YOLO26 pose runs on the MLA. Keypoints drive this measured lean gauge. Fifty-five percent is a GUESS for this prototype, not a validated threshold.”

## Beat 3 — red flip (0:48–1:08)

**Show:** Hold the bend through the **8-frame window (GUESS)**. Show the fall event and `index.html` going red.

**Say:**

“After an eight-frame GUESS window, Watch emits a possible-fall event and the family page turns red. This morning a real body drove this state for the first time: 63% peak lean MEASURED, 58-frame streak MEASURED, 0.916 confidence MEASURED, and 8.1 to 8.3 milliseconds per frame MEASURED. This is a prototype trigger, not a medical claim.”

## Beat 4 — ledger + numbers before the fall (1:08–1:43)

**Show:** Session ledger: frames processed, `pixel_bytes`, NIC receive/transmit bytes, `uploaded 0`, and `stored 0`; then its `trend` line and the “Before the fall” panel.

```sh
cat /sys/class/net/end0/statistics/tx_bytes
```

**Say:**

“The application ledger accounts for every processed frame and reports zero uploaded and zero stored. B′ adds computed decoded pixel bytes and measured NIC receive and transmit bytes. The serial counter is the judge’s independent one-line check.”

“A fall alert is table stakes. Watch's product is the numbers before the fall: last sit-to-stand seconds and session count, floor-lie now and total, upright, sitting, and floor seconds, and company seconds with at least two people. They are computed on the MLA from keypoints; only numbers leave. They ride the same ledger as the `trend` stdout line and the `trend` key in `session-ledger.json`, and the same bytes-out counter.”

“The trend code is on main in `perception/watch_events.py`, commit `1ccc396`; `demo.html` renders this panel, commit `f15fd04`. Values are measured live when running; no capture is committed. Thresholds are guessed, and interface/trend.html is a 30-day fixture landing from another lane. The other fall detector cannot show the week before.”

“the counter proves the board leaked nothing; in the demo the camera is the Mac.”

## Beat 5 — phone page (1:43–2:00)

**Show:** **If the hotspot is up; otherwise the same page on the Mac:** use `interface/serve-phone.sh`, open the family alert page, and point to its receipt card; otherwise show `index.html` on the Mac.

**Say:**

“The alert goes to family first. There is no monitoring centre and no automatic 911 call. The family keeps the context without receiving a clip or gaining a video archive.”

## If asked

- **Is the fall detector validated?** “No. Lean is calculated from live pose keypoints; the 55% threshold and eight-frame window are GUESS demo parameters. Calibration and field validation are roadmap.”
- **Are the trend numbers validated?** “No. The values are measured live from keypoints on the MLA, and only numbers leave, but there is no committed trend-line capture. The v1 thresholds are GUESSED: sitting means hips below 0.65 with an upright torso; floor means hips and shoulders below 0.85 for at least 2 seconds; company means at least two people. The published 5× sit-to-stand over 15 seconds is an anchor; ours is one rep and unvalidated. The 30-day view is a FIXTURE.”
- **What is the 15.2 KB?** “It is MEASURED `end0` transmit traffic across all protocols at the 60-frame snapshot, before quiet mode. It includes the SSH session carrying per-frame diagnostics. Quiet mode was separately MEASURED live this morning at 10.0 KB out for 150 frames; the committed captures are pre-quiet-mode.”
- **Why is the camera a Mac?** “This prototype uses the Mac as its camera and sends that stream to Modalix. The counter proves the board leaked nothing; in the demo the camera is the Mac.”
- **Why family first?** “The family knows the person and context. We intentionally do not automate 911.”
- **What about wandering?** “An earlier demo called movement ‘wander’; that was a heuristic, not validated behavior understanding, so we do not lead with it.”
- **What did Dave say?** “Dave from SiMa said fall detection was one of the first things he thought about in senior centers, called it a selling feature, and warned us: ‘don’t try to make the product.’ We proved one honest path.”

## Failure rule

If live inference fails, say so once. Open `pitch/backup/index.html`, call it a FIXTURE replay, and use it only to explain the family interaction. Never present it as hardware evidence. Do not substitute an old quiet-mode transmit claim: show the available measured capture and state its pre-quiet-mode boundary.
