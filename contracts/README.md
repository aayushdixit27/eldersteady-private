# contracts/

Architect-owned. **No lane edits anything in this directory.**

`event.schema.json` is the single interface between perception and everything
downstream. `fixtures/events.sample.jsonl` is hand-written — it was authored
before any model ran, so lanes 2 and 3 can start at minute 0 and never wait on
lane 1.

The fixture deliberately contains cases that are awkward on purpose:

- **11:47:33 / 11:47:36 bathroom** — the same fall reported twice, first below
  any sane threshold then above it. The "gentle crumple" the Reddit evidence
  says existing sensors miss looks exactly like this. Downstream must decide
  whether that is one incident or two.
- **04:11–04:14** — a wander that ends in a low-confidence fall. Four events,
  one story. Alerting on each separately is how you build the thing the
  evidence says caregivers already threw away.
- **18:20 / 18:50 kitchen** — a stove event that is still true thirty minutes
  later. Escalation, not a new incident.
- **confidence 0.34 and 0.41** — below where you would want to wake a family
  member. Suppressing them silently is the failure this project cannot ship.

If a lane believes the schema is wrong, that is a finding, not an edit.
