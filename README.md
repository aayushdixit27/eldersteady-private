# Watch

## Know they may need help. Never gain the ability to watch.

Watch is a family-first fall alert that runs inside the home. A live Mac camera feeds a Modalix MLSoC over UDP; YOLO26 runs on the MLA; the system measures body lean from pose keypoints; and a sustained lean turns the family alert page red.

No clip is saved. No frame is uploaded. No call centre watches. Watch tells family first and does not call 911.

> “Fall detection was one of the first things I thought about in senior centers.”
>
> “It’s a selling feature.”
> — Dave, SiMa mentor

## The live path we built

**Mac camera → UDP → Modalix → YOLO26 pose → measured lean → fall event → family alert**

The live demo runs YOLO26 pose on the Modalix MLA at **8–9 ms per frame**. Each frame produces keypoints; Watch derives a torso-lean value from those keypoints and displays it as a live gauge. When lean remains above the configured threshold for the configured number of consecutive frames, Watch emits a possible-fall event. The family page immediately flips red.

YOLO26 detection is also available on the same board path. It proves the live camera-to-MLA pipeline; pose supplies the keypoints used by the current fall demo.

This is a prototype trigger, not a medical claim. The lean value is measured from model keypoints. The current **55% lean threshold** and **8-frame window** are demo parameters and have not been validated in homes or senior centers. “Wander” in an earlier build was a heuristic, not a validated behavior classifier. Calibration is roadmap, not something we pretend to have finished.

As Dave advised: **“Don’t try to make the product.”** We built the one decisive path and made its limits visible.

## Privacy you can inspect

Privacy is usually a promise. Watch makes it an accounting invariant. Every live session writes a ledger with:

```json
{
  "frames_processed": 30,
  "frames_in_events": 0,
  "frames_unattributed": 30,
  "events_emitted": 0,
  "frames_stored": 0,
  "frames_uploaded": 0
}
```

`frames_processed = frames_in_events + frames_unattributed`. Event or no event, every processed frame is accounted for. In the measured session above, **uploaded = 0** and **stored = 0**.

The application is installed on board-local storage. It has run successfully with the Mac-served NFS workspace unmounted. That matters because “on device” should survive more than a network diagram: the app and model do not depend on a mounted development machine.

## Why this wins even against another fall detector

Fall detection is the entry point, not the differentiation. Watch proves something a conventional camera cannot: **nothing left the room**.

- The live ledger accounts for processed, event-associated, and unattributed frames, with zero uploaded and zero stored.
- The alert goes to family first; there is no monitoring centre and no automatic 911 call.
- The parent wears nothing, installs nothing, and has no new screen to operate.
- There is no video archive for a family member, vendor, or attacker to browse later.

The product is a different agreement between a parent and their family: know when help may be needed without acquiring surveillance.

## Three-beat demo

1. **See it happen.** Live camera, live lean gauge, 8–9 ms MLA inference. Sustain a lean for eight frames; the fall event fires and the family alert flips red.
2. **Pull the dependency.** From the serial console, show the board-local application continuing with the Mac disconnected and NFS unavailable.
3. **Act as family.** Return to the red alert screen: a possible fall, a family response, and a session ledger showing zero frames stored and zero uploaded.

The demo is intentionally narrow. It does not establish fall-detection accuracy, clinical safety, alert-delivery reliability, or validated thresholds. Those require representative homes, consented trials, calibration, and measurement of false alerts and missed staged events.

## Run the live demo

The operator runbook is [`perception/DEMO.md`](perception/DEMO.md). The live launcher is [`perception/live_demo.sh`](perception/live_demo.sh); the family view is [`interface/index.html`](interface/index.html). A clearly labelled fixture-only backup remains in [`pitch/backup/index.html`](pitch/backup/index.html), but it is not the product proof.

**Watch — care without surveillance.**
