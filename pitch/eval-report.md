# Fixed eval report — round 2

Run on 15 September 2026 against the merged tree. Items 1–5 use the hand-written `contracts/fixtures/events.sample.jsonl`; their counts are fixture-derived, not hardware measurements. Item 6 uses the setup lane's dated hardware observation.

```text
$ python3 -m evidence < contracts/fixtures/events.sample.jsonl
inc-0002 fall bathroom ... severity=urgent event_count=2 frames_never_stored=47952
inc-0003 stove_unattended kitchen ... severity=urgent event_count=2 frames_never_stored=264300 state=escalated
inc-0004 wander front_door ... severity=urgent event_count=4 frames_never_stored=333540

$ python3 -m unittest discover -s evidence -p 'test_*.py'
Ran 5 tests in 0.002s
OK
```

| # | Fixed item | Result | Output/evidence |
|---|---|---|---|
| 1 | 04:11–04:14 produces one incident, not four | **Pass** | Fixture-derived `inc-0004` has `event_count: 4`, one output incident, and the 04:11:52–04:14:02 boundaries. |
| 2 | Bathroom 11:47:33 and 11:47:36 produce one urgent incident | **Pass** | Fixture-derived `inc-0002` is one `urgent` incident with `event_count: 2`. |
| 3 | Kitchen 18:20 and 18:50 produce one escalating incident | **Pass** | Fixture-derived `inc-0003` is one incident with `event_count: 2`, `severity: urgent`, and `state: escalated`. |
| 4 | Confidence below 0.5 remains human-findable | **Pass** | Both fixture events are retained in human-facing incidents: 11:47:33 is the bathroom incident's `opened_ts`; 04:14:02 is the night incident's `last_ts`. The technical fixture preserves their 0.34 and 0.41 confidence values. |
| 5 | Closed incident ledger equals exact event sum | **Pass** | The only render path computes `frames_never_stored` with integer `sum(event["discarded_frames"] ...)`; fixture outputs equal 47,952, 264,300, and 333,540 exactly. The fixture has no `closed` state, so this validates the ledger computation used by every rendered state rather than a close transition. |
| 6 | App runs from board-local storage with Mac link down | **Pass** | Measured on Modalix hardware by setup lane: with `/workspace` unmounted, `/home/sima/watch-perception/run_board_local.sh` emitted one event with `discarded_frames: 1` and exited 0; runtime package path was NVMe. |

## Verdict

**6 pass · 0 fail · 0 not yet testable.** Five passes are fixture-backed software evaluation; one is measured board-local hardware execution. This does not establish live-model accuracy, alert delivery, field reliability, or a hardware-measured 333,540-frame ledger.

## Reproduction notes

The package command succeeds from repository root. The documented discovery command also succeeds. `python3 -m unittest -v evidence.test_incidents` fails because the test imports `incidents` as a top-level module; this does not affect the documented test command or runtime package, but it is a packaging defect worth fixing later.
