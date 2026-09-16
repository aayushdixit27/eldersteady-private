# Rhythm evidence
Run `python3 -m evidence.rhythm --log interface/live/board.log --out interface/live/day.json`.
The process rereads the log and atomically refreshes `day.json` every ten seconds.
Add `--once` for a single refresh or `--start 2026-09-16T07:00:00-07:00` to anchor sample zero.
Each trend sample contributes posture and the nearest preceding frame's pose count to its wall-clock minute.
Minutes summarize dominant posture, company, first presence, totals, and contract-defined visits.
