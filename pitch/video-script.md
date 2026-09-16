# Submission video — 4:30 maximum

Export at **4:30 or shorter**. Burn in the labels “LIVE,” “MEASURED FROM KEYPOINTS,” “UNVALIDATED DEMO PARAMETERS,” and “0 UPLOADED · 0 STORED” where specified.

| Time | Picture | Voiceover / live words |
|---|---|---|
| 0:00–0:25 | Parent at home; no wearable or screen. Title: “Know they may need help. Never gain the ability to watch.” | “Families supporting an aging parent face a bad bargain: learn too late that help was needed, or install a camera someone can watch. Watch creates a third option: a family-first alert with no video leaving the room.” |
| 0:25–0:45 | Modalix and Mac camera in the same shot. Animate the real path: camera → UDP → Modalix → family alert. | “A live Mac camera sends video over UDP to Modalix. The board interprets it locally and sends an event—not a video—to the family view.” |
| 0:45–1:25 | Uncut live screen capture: upright person, moving lean gauge, frame lines showing 8–9 ms. Captions: “LIVE” and “MEASURED FROM KEYPOINTS.” | “YOLO26 pose runs on the MLA at eight to nine milliseconds per frame. The model returns body keypoints. Watch calculates per-frame torso lean from them, so the gauge is a measurement, not a staged animation.” |
| 1:25–1:52 | Person leans and holds; counter reaches eight; possible-fall banner appears and family page flips red. Caption: “55% FOR 8 FRAMES · UNVALIDATED DEMO PARAMETERS.” | “For this prototype, lean above fifty-five percent for eight consecutive frames emits a possible-fall event. The family page turns red. The lean is measured; that threshold and window are not field-validated, and this is not a medical claim.” |
| 1:52–2:15 | Dave quote cards over senior-center context; attribute “Dave · SiMa mentor.” | “SiMa mentor Dave said, ‘fall detection was one of the first things I thought about in senior centers.’ He called it ‘a selling feature’—and gave us the right scope: ‘don’t try to make the product.’ Calibration is roadmap; today we prove the decisive path.” |
| 2:15–2:55 | Serial terminal and physical unplug. Show NFS unavailable, then the board-local command running. Caption: “BOARD-LOCAL · NFS UNMOUNTED.” | “Now we remove the development machine. Unplugging the Mac also removes its NFS workspace. Over serial, the application and model still run from board-local storage. The intelligence is in the room, not hiding behind a cloud connection.” |
| 2:55–3:30 | Ledger fills screen. Highlight the equality and both zeroes. | “Privacy is an absence, so Watch makes it countable. Every session records frames processed, frames in events, and frames unattributed. Those categories reconcile. This measured session shows zero frames uploaded and zero frames stored.” |
| 3:30–3:55 | Red family page: possible fall and family response. Cross out call centre and 911 auto-dial icons. | “The alert goes to family first. Watch does not send a clip to a monitoring centre and does not automatically call 911. The family gets the signal and keeps the context.” |
| 3:55–4:18 | Split comparison: “fall detector” vs “Watch”; on Watch side show ledger, family, zero/zero. | “Another team may also detect a fall. Our differentiation is what cannot be seen in a detection box: we prove nothing left the room. The ledger, family-first response, and no video archive change the agreement between parent and family.” |
| 4:18–4:30 | Product name and red alert resolving to calm screen. End card: “Watch · care without surveillance.” | “Know when help may be needed without gaining the ability to watch. Watch: care without surveillance.” |

## Truth checklist before export

- The camera-to-board footage is a real live run, not the fixture backup.
- Say “YOLO26 pose on the MLA at 8–9 ms per frame,” not “validated fall detection at 8–9 ms.”
- Lean is measured from keypoints. The 55% threshold and eight-frame window are unvalidated.
- Do not claim the video stream continues after unplugging its Mac source. Show via serial that the board-local app/model remain runnable with NFS unavailable.
- Show the ledger field names and the actual measured values; do not substitute fixture totals.
- “Wander” was a heuristic. Do not describe it as validated scene understanding.
- No accuracy, safety, clinical, field-validation, automatic-911, or guaranteed-alert claim.
