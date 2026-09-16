# Evidence incident processor

Read event JSONL on standard input and write incident JSONL on standard output:

```sh
python3 evidence/incidents.py < contracts/fixtures/events.sample.jsonl
```

The processor uses only the Python standard library. It validates every event,
sorts timestamped input deterministically, groups event trails, and derives
`frames_never_stored` solely by exact addition of `discarded_frames`.

Run the fixture checks with:

```sh
python3 -m unittest discover -s evidence -p 'test_*.py'
```
