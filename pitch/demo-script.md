# Live demo — three beats, about 2 minutes

Before presenting: open the family alert page and a large terminal running `perception/live_demo.sh`. Confirm pose mode, the camera preview, the lean gauge, and serial access. Keep the fixture backup closed unless the live path fails.

## Beat 1 — camera, gauge, fall flip (0:00–0:55)

**Show:** Stand upright in the live Mac camera. Point to the terminal: frame count, pose/lean, and 8–9 ms MLA time. Lean far enough to cross the gauge; hold for eight frames. Show the fall banner and family page turning red.

**Say:**

“This is live video from this Mac, sent over UDP to the Modalix beside us. YOLO26 pose is running on the MLA at eight to nine milliseconds per frame. These keypoints produce the lean gauge you see moving now.”

“Lean is measured. The policy around it is not yet validated: for this demo, fifty-five percent for eight consecutive frames emits a possible-fall event. There it is—and the family screen turns red. This is a prototype trigger, not a diagnosis.”

## Beat 2 — pull the Mac, keep the board (0:55–1:25)

**Show:** Put the serial console full-screen. Disconnect the Mac link. Show NFS unavailable and the board-local application/model continuing or launching from board-local storage. Do not imply that the Mac camera stream continues after its source is unplugged.

**Say:**

“Now the proof that separates Watch from another fall-detection demo. I’m unplugging the Mac—the development workspace and its NFS mount disappear with it. Over serial, the application still runs from board-local storage. In production the camera is local to the unit; this test proves the intelligence does not depend on a cloud or development mount.”

## Beat 3 — alert and privacy ledger (1:25–2:00)

**Show:** Reconnect if needed and return to the red family alert. Point to the family action, then the session ledger: `frames_processed`, `frames_in_events`, `frames_unattributed`, `frames_uploaded: 0`, `frames_stored: 0`.

**Say:**

“The family gets a possible-fall alert first. Watch does not call a monitoring centre or 911. And this ledger makes the privacy claim inspectable: every processed frame is either in an event or unattributed; zero were uploaded and zero were stored.”

“Another team may detect a fall. We prove nothing left the room. That is care without surveillance.”

## If asked

- **Is the fall detector validated?** “No. Lean is calculated from live pose keypoints; the 55% threshold and eight-frame window are unvalidated demo parameters. Calibration and field validation are roadmap.”
- **What about wandering?** “An earlier demo called movement ‘wander’; that was a heuristic, not validated behavior understanding, so we do not lead with it.”
- **Why family first?** “The family knows the person and context. We intentionally do not automate 911.”
- **What did the mentor say?** “Dave from SiMa said fall detection was one of the first things he thought about in senior centers, called it a selling feature, and warned us: ‘don’t try to make the product.’ We followed that advice by proving one honest path.”

## Failure rule

If live inference fails, say so once. Open `pitch/backup/index.html`, call it a fixture replay, and use it only to explain the family interaction. Never present it as hardware evidence. The board-local/NFS proof and measured session ledger remain separate evidence.
