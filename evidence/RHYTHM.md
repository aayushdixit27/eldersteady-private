# Rhythm evidence
Run `python3 -m evidence.rhythm --log interface/live/board.log --out interface/live/day.json`.
The process rereads the log and atomically refreshes `day.json` every ten seconds.
Add `--once` for a single refresh or `--start 2026-09-16T07:00:00-07:00` to anchor sample zero.
Each trend sample contributes posture and the nearest preceding frame's pose count to its wall-clock minute.
Minutes summarize dominant posture, company, first presence, totals, and contract-defined visits.
Three consecutive night minutes of standing, or alternating standing/absent states, add one
`wander` event to both `board.log` and `day.json`; a continuing episode is not repeated and
separate episodes have a 30-minute cooldown. The default local night is `23:00-06:00`,
configurable with `WATCH_NIGHT`. `WATCH_CLOCK_OFFSET_MIN` shifts only the night test for demos;
events produced with that override are always labelled `"demo_clock":true`.
