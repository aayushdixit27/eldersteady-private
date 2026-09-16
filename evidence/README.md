# Evidence incident processor

Run the five fixture checks:

```sh
python3 -m unittest discover -s evidence -p 'test_*.py'
```

- `test_mission_fixture`
- `test_ledger_is_exact_for_every_incident`
- `test_low_confidence_events_are_surfaced`
- `test_arrival_order_does_not_change_output`
- `test_interleaved_event_does_not_split_stove_incident`

Read event JSONL on standard input and write incident JSONL on standard output:

```sh
python3 -m evidence < contracts/fixtures/events.sample.jsonl
```

The processor uses only the Python standard library. It validates every event,
sorts timestamped input deterministically, groups event trails, and derives
`frames_never_stored` solely by exact addition of `discarded_frames`.
