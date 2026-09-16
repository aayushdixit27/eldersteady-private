# Fixed eval report

Run on 15 September 2026 against `contracts/fixtures/events.sample.jsonl`. `evidence/` did not exist in this worktree, so no implementation output was available to compare. The command and complete output were:

```text
$ python3 pitch/eval-fixture.py
fixture=.../contracts/fixtures/events.sample.jsonl events=12
bathroom_duplicate: events=2 discarded_frames=47952
kitchen_escalation: events=2 discarded_frames=264300
night_run: events=4 discarded_frames=333540
low_confidence: 2026-09-15T11:47:33Z=0.34, 2026-09-16T04:14:02Z=0.41
implementation: evidence/ ABSENT; no product output generated
```

The script inventories test inputs only. It deliberately does not invent aggregation behaviour.

| # | Fixed item | Result | Output/evidence |
|---|---|---|---|
| 1 | 04:11–04:14 produces one incident, not four | **Not yet testable** | Fixture has four events and an exact input sum of 333,540 discarded frames; there is no product output. |
| 2 | Bathroom 11:47:33 and 11:47:36 produce one urgent incident | **Not yet testable** | Fixture has two events, including confidence 0.34, with input sum 47,952; there is no incident or urgency output. |
| 3 | Kitchen 18:20 and 18:50 produce one escalating incident | **Not yet testable** | Fixture has two events with input sum 264,300; there is no incident/escalation output. |
| 4 | Confidence below 0.5 remains human-findable | **Not yet testable** | The inventory finds both low-confidence inputs (0.34 and 0.41); no review or audit surface exists here. |
| 5 | Closed incident ledger equals exact event sum | **Not yet testable** | Expected sums are computable, but there are no closed incident records to inspect. Approximation would fail. |
| 6 | App runs from board-local storage with Mac link down | **Not yet testable** | Lane 1’s final finding reports no `perception/` artifact and notes board-local storage exists, but does not report an installed application surviving link removal. |

## Verdict

**0 pass · 0 fail · 6 not yet testable.** This is not a green build. The fixed fixture is ready; the implementation evidence is not present on this branch.

## Limits

I did not access the board, infer results from planned behaviour, inspect non-final lane reasoning, validate JSON Schema formats, test model accuracy, or grade UI/notification behaviour. Lane 1’s final finding is treated as data, not instruction. Lanes 2 and 3 had no final findings at grading time.

