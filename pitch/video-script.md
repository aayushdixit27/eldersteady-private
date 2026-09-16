# Submission video — 5:00 maximum, 4:30 target

California will not let a facility put a camera in her room; at home the same question is yours — this is a fall alert that answers it in bytes.

Export at **5:00 maximum**; target **4:30**. Wherever a number appears, burn in its provenance: **MEASURED**, **COMPUTED**, or **GUESS**.

| Time | Picture | Voiceover / live words |
|---|---|---|
| 0:00–0:25 | Parent-at-home context; the opening sentence fills the screen. Small source line: “CDSS PIN 15-RM-01 · resident-room cameras require Licensing waiver · no analytics-only exemption.” | “California will not let a facility put a camera in her room; at home the same question is yours — this is a fall alert that answers it in bytes.” |
| 0:25–0:58 | `demo.html` counter running. Keep field labels and burn-ins visible: “60 FRAMES · MEASURED,” “165.9 MB PIXELS · COMPUTED,” “2.55 MB VIDEO IN · MEASURED,” “15.2 KB OUT · MEASURED, PRE-QUIET-MODE,” “1 : 168 · COMPUTED.” | “Start with the accounting. At 60 frames MEASURED, the board decoded 165.9 megabytes COMPUTED, received 2.55 megabytes MEASURED, and sent 15.2 kilobytes MEASURED: a 1-to-168 ratio COMPUTED. That transmit count is all protocols and predates quiet mode, so it includes SSH per-frame diagnostics. We do not claim the unmeasured quiet-mode figure.” |
| 0:58–1:28 | Modalix and Mac together; uncut live camera and moving gauge. Person bends. Burn in: “LIVE,” “LEAN · MEASURED FROM KEYPOINTS,” “55% THRESHOLD · GUESS.” | “The Mac camera streams over UDP to Modalix. YOLO26 pose runs on the MLA, and keypoints drive measured torso lean. The 55% trigger threshold is a GUESS, not a validated clinical boundary.” |
| 1:28–1:55 | Hold the bend through the counter; possible-fall event appears and `index.html` flips red. Burn in: “8-FRAME WINDOW · GUESS,” “PROTOTYPE TRIGGER · NOT A MEDICAL CLAIM.” | “Hold through an eight-frame GUESS window and a possible-fall event flips the family page red. Until this morning only simulated logs had driven red. Now a real body has.” |
| 1:55–2:28 | Evidence excerpt beside the live shot. Burn in each: “2026-09-16 08:03 PDT · MEASURED,” “63% PEAK · MEASURED,” “58 FRAMES · MEASURED,” “0.916 · MEASURED,” “157 DISCARDED · MEASURED,” “8.1–8.3 MS/FRAME · MEASURED.” | “At 08:03 PDT MEASURED, the first real fall peaked at 63% lean MEASURED, held a 58-frame streak MEASURED, emitted 0.916 confidence MEASURED after 157 discarded frames MEASURED, and ran at 8.1 to 8.3 milliseconds per frame MEASURED.” |
| 2:28–3:13 | Ledger fills the screen: frames processed, `pixel_bytes`, NIC receive/transmit, uploaded zero, stored zero. Then serial shows `cat /sys/class/net/end0/statistics/tx_bytes`. Burn in provenance beside every value. | “The session ledger accounts for processed frames and reports zero uploaded MEASURED and zero stored MEASURED at the application boundary. B′ adds decoded pixel bytes COMPUTED and NIC receive and transmit bytes MEASURED. Over serial, one line lets the judge read transmit bytes directly. the counter proves the board leaked nothing; in the demo the camera is the Mac.” |
| 3:13–3:42 | Phone opens the red family page over the Mac hotspot. Overlay: “IF HOTSPOT IS UP · OTHERWISE SAME PAGE ON MAC.” Cross out monitoring-centre and 911 auto-dial icons. | “The alert goes to family first. There is no monitoring centre and no automatic 911 call. The family gets the signal without a clip or archive.” |
| 3:42–4:08 | Dave quote cards, attributed “Dave · SiMa mentor.” | “SiMa mentor Dave said fall detection was one of the first things he thought about in senior centers. He called it a selling feature, then gave us the scope: ‘don’t try to make the product.’” |
| 4:08–4:30 | Split: generic fall detector versus Watch ledger and family page. End card: “Watch · care without surveillance.” | “Another team also does fall detection — differentiate on the ledger. Watch changes the agreement: know they may need help without gaining the ability to watch. Care without surveillance.” |

## Truth checklist before export

- The camera-to-board footage is a real live run, not the fixture backup.
- Every displayed number carries a MEASURED, COMPUTED, or GUESS burn-in.
- The counter shows video in, bytes out, pixels decoded, and ratio; **15.2 KB is MEASURED pre-quiet-mode all-protocol traffic**, including SSH diagnostics. Do not show a quiet-mode transmit figure until it is measured live.
- Say “YOLO26 pose on the MLA at 8.1–8.3 ms per frame MEASURED in the first real-fall capture,” not “validated fall detection.”
- Lean is measured from keypoints. The 55% threshold and eight-frame window are GUESS parameters.
- The first red-state proof is a real body on camera; earlier red-state logs were simulated.
- Show ledger field names and actual values. Uploaded zero and stored zero are application-boundary measurements; NIC bytes are the external counter.
- Include verbatim: “the counter proves the board leaked nothing; in the demo the camera is the Mac.”
- This is a prototype trigger, not a medical claim. No accuracy, safety, clinical, field-validation, automatic-911, monitoring-centre, or guaranteed-alert claim.
- “Wander” was a heuristic. Do not describe it as validated scene understanding.
