# watch

## Care without surveillance.

`watch` is a room camera for families supporting an aging parent. It recognizes a fall, night wandering, or an unattended stove; tells the family once; and destroys every frame on the device.

> **0 frames uploaded. 333,540 frames never stored.**

That second number is the product. Ordinary cameras ask a parent to trade privacy for safety. `watch` turns privacy from a promise into a ledger: every processed-and-discarded frame is counted, incident by incident, while raw images remain in the room.

## The moment that matters

At 4:11 a parent leaves the bedroom, passes through the kitchen and reaches the front door. Four model events could become four noisy alerts. `watch` groups them into one story for the family:

> **Night wandering · urgent**  
> Bedroom → kitchen → front door · 04:11–04:14  
> 333,540 frames never stored · 0 frames uploaded

The family gets context they can act on, not a call-centre transcript. The parent installs no app, wears nothing, and is never asked to operate a screen.

## Why on-device AI

This is not motion detection. The same movement can mean an ordinary trip to the kitchen, a sustained night-wandering episode, or a fall. A vision-language model supplies scene-level meaning; temporal incident logic joins repeated observations; the Modalix MLSoC keeps that interpretation local. The target hardware runs vision-language models on-device at under 10 W and up to 50 TOPS.

## What happens after “yes”

1. The family chooses three rooms and adds trusted contacts.
2. A local installer positions a camera and runs three staged checks: fall, night route, stove.
3. The family reviews which situations are urgent and who is told first.
4. For two weeks, low-confidence observations remain visible for review while alert rules are tuned.
5. Each month, the family can read the privacy ledger without opening or exporting video—because there is no stored video to open.

The initial user is an adult child coordinating care for a parent who wants to remain at home but rejects cloud cameras or wearables. The capability they buy is not “faster alerts”; it is a new agreement: the family can know when help may be needed without being able to watch.

## Why now—without invented urgency

Over a 30-day trial, acting now creates a tested escalation plan and a visible ledger of discarded frames. Waiting preserves today’s privacy, but the existing gap remains: the family still learns about a fall, wandering episode, or stove risk through a phone call, a neighbour, or the next visit. We do not claim a measured incident rate or pretend every family needs this immediately.

## Built for the demo path

The fixed evaluation fixture covers duplicate falls, a multi-room night episode, a continuing stove event, and low-confidence evidence. The required standard is exact: related events become one incident; suppressed observations remain findable; and a closed incident’s `frames_never_stored` equals the exact sum of its events’ `discarded_frames`.

Open [`pitch/backup/index.html`](pitch/backup/index.html) to rehearse the complete offline demo with no board, server, network, or install. The backup is clearly labelled simulated fixture replay.

## What is real—and what remains unproven

The event contract and hand-written adversarial fixture are present. At the time this page was written, this worktree contained no merged perception, evidence, or interface implementation, so the six fixed evals could not be passed here. Board-local execution, live model accuracy, the UI, alerts, and incident aggregation must be demonstrated by their owning lanes before they are claimed. The offline backup is a pitch-resilience artifact, not proof of hardware execution. We make no medical, diagnostic, prevalence, or safety guarantee.

