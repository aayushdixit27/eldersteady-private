# Submission video — 5:00 maximum, 4:30 target

California will not let a facility put a camera in her room; at home the same question is yours — this is a fall alert that answers it in bytes.

Export at **5:00 maximum**; target **4:30**. Wherever a number appears, burn in its provenance: **MEASURED**, **COMPUTED**, **GUESS**, or **FIXTURE**.

| Time | Picture | Voiceover / live words |
|---|---|---|
| 0:00–0:25 | Parent-at-home context; the opening sentence fills the screen. Source line: “CDSS PIN 15-RM-01 · resident-room cameras require Licensing waiver · no analytics-only exemption.” | “California will not let a facility put a camera in her room; at home the same question is yours — this is a fall alert that answers it in bytes.” |
| 0:25–0:58 | `demo.html` counter running. Keep field labels and burn-ins visible: “60 FRAMES · MEASURED,” “165.9 MB PIXELS · COMPUTED,” “2.55 MB VIDEO IN · MEASURED,” “15.2 KB OUT · MEASURED, PRE-QUIET-MODE,” “1 : 168 · COMPUTED.” | “Start with the accounting. At 60 frames MEASURED, the board decoded 165.9 megabytes COMPUTED, received 2.55 megabytes MEASURED, and sent 15.2 kilobytes MEASURED: a 1-to-168 ratio COMPUTED. That transmit count is all protocols and predates quiet mode, so it includes SSH per-frame diagnostics. Capture 0833 measured quiet mode at 11.1 kilobytes out at frame 150: 1 to 303 COMPUTED.” |
| 0:58–1:28 | Modalix and Mac together; uncut live camera and moving gauge. Person bends. Burn in: “LIVE,” “LEAN · MEASURED FROM KEYPOINTS,” “55% THRESHOLD · GUESS.” | “The Mac camera streams over UDP to Modalix. YOLO26 pose runs on the MLA, and keypoints drive measured torso lean. The 55% trigger threshold is a GUESS, not a validated clinical boundary.” |
| 1:28–1:55 | Hold the bend through the counter; possible-fall event appears and `index.html` flips red. Burn in: “8-FRAME WINDOW · GUESS,” “PROTOTYPE TRIGGER · NOT A MEDICAL CLAIM.” | “Hold through an eight-frame GUESS window and a possible-fall event flips the family page red. Until this morning only simulated logs had driven red. Now a real body has.” |
| 1:55–2:28 | Evidence excerpt beside the live shot. Burn in each: “2026-09-16 08:03 PDT · MEASURED,” “63% PEAK · MEASURED,” “58 FRAMES · MEASURED,” “0.916 · MEASURED,” “157 DISCARDED · MEASURED,” “8.1–8.3 MS/FRAME · MEASURED.” | “At 08:03 PDT MEASURED, the first real fall peaked at 63% lean MEASURED, held a 58-frame streak MEASURED, emitted 0.916 confidence MEASURED after 157 discarded frames MEASURED, and ran at 8.1 to 8.3 milliseconds per frame MEASURED.” |
| 2:28–2:58 | Ledger fills the screen: frames processed, `pixel_bytes`, NIC receive/transmit, uploaded zero, stored zero; show the `trend` stdout line beside it. Then serial shows `cat /sys/class/net/end0/statistics/tx_bytes`. Burn in provenance beside every value. | “The ledger reports zero uploaded MEASURED and zero stored MEASURED. It carries NIC bytes MEASURED, decoded pixels COMPUTED, and the trend line. Over serial, the judge reads transmit bytes directly. the counter proves the board leaked nothing; in the demo the camera is the Mac.” |
| 2:58–3:28 | One shot of the live “Before the fall” panel. Optional posture-test-4 inset; burn in: “1 CONTROLLED TEST · 1 PERSON,” “VALUES · MEASURED,” “THRESHOLDS · GUESS.” | “A fall alert is table stakes. ElderSteady Private adds posture, sit-to-stand, floor and company numbers computed on the MLA. Posture test 4 read all five tested states with real xyxy boxes: one controlled test with one person, not validation; tests 1 through 3 missed chair or floor.” |
| 3:28–3:43 | Dedicated shot of interface/trend.html. Full-width burn-in: “30-DAY VIEW · FIXTURE.” Secondary burn-in: “THRESHOLDS · GUESS.” | “The thresholds are GUESSED v1 rules. Sitting is hips below 0.65 with an upright torso; floor is hips and shoulders below 0.85 for at least two seconds; company is at least two people. The published five-rep sit-to-stand over 15 seconds is an anchor; ours is one rep and unvalidated. This 30-day view is a FIXTURE.” |
| 3:43–4:00 | Phone opens the red family page via `interface/serve-phone.sh`; hold on the receipt card. Overlay: “IF HOTSPOT IS UP · OTHERWISE SAME PAGE ON MAC.” | “The alert goes to family first. Its receipt accounts for the alert without a clip or archive. There is no monitoring centre and no automatic 911 call.” |
| 4:00–4:15 | Dave quote cards, attributed “Dave · SiMa mentor.” | “Dave called fall detection a selling feature, then gave us the scope: ‘don’t try to make the product.’” |
| 4:15–4:30 | Split: generic fall detector versus ElderSteady Private trend, ledger, and family page. End card: “ElderSteady Private · care without surveillance.” | “The other fall detector cannot show the week before. ElderSteady Private can show the numbers without giving the family a camera view.” |

## Truth checklist before export

- The camera-to-board footage is a real live run, not the fixture backup.
- Every displayed number carries a MEASURED, COMPUTED, or GUESS burn-in.
- The counter shows video in, bytes out, pixels decoded, and ratio; **15.2 KB is MEASURED pre-quiet-mode all-protocol traffic**, including SSH diagnostics. Quiet mode MEASURED 1 : 303 at frame 150 and 1 : 98 over 13,350 frames (same capture); say the long-run number, not only the snapshot..
- Say “YOLO26 pose on the MLA at 8.1–8.3 ms per frame MEASURED in the first real-fall capture,” not “validated fall detection.”
- Lean is measured from keypoints. The 55% threshold and eight-frame window are GUESS parameters.
- The first red-state proof is a real body on camera; earlier red-state logs were simulated.
- Show ledger field names and actual values. Uploaded zero and stored zero are application-boundary measurements; NIC bytes are the external counter.
- Include verbatim: “the counter proves the board leaked nothing; in the demo the camera is the Mac.”
- Show the live “Before the fall” panel: posture test 4 values are MEASURED in `evidence/captures/2026-09-16-1012-posture-test-4-xyxy.txt`; thresholds are GUESS. Burn in “1 CONTROLLED TEST · 1 PERSON,” and note that tests 1–3 missed chair or floor.
- Say both halves: computed on the MLA, only numbers leave; thresholds are GUESS, and interface/trend.html is a 30-day FIXTURE landing from another lane.
- This is a prototype trigger, not a medical claim. No accuracy, safety, clinical, field-validation, automatic-911, monitoring-centre, or guaranteed-alert claim.
- “Wander” was a heuristic. Do not describe it as validated scene understanding.
