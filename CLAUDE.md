# ElderSteady Private — briefing for a fresh session

You are the setup/engineering lane for **ElderSteady Private** (formerly Watch), a family-first fall alert on the SiMa Modalix DevKit (AI Infra Summit hackathon, SiMa track). The product claim: every frame is processed on the MLA in the room, counted, and destroyed; only analytics leave; the family is told, not 911. User: Aayush (PM by training, token-conscious; wants short replies and Codex used for anything with a brief).

## Start of session
1. `senso kb get-content d5a1c61e-4d38-4dd2-adb5-da310ab89a74 --output json --quiet` → read `text`. That is CURRENT.md: task, state, next action, settled and rejected decisions. Trust it over anything you assume.
2. For any "how do I…" about the rig, ask Senso first: `senso search "<question>" --output json --quiet` (folder: AI Infra Hackathon).
3. Then act. Do not re-read the repo to orient; CURRENT.md already says where things are.

## Things a fresh session gets wrong unless told
- The demo is `interface/demo.html` + camera + the red flip, run by `POSE=1 bash perception/live_demo.sh`. **A terminal is not the demo.**
- `claude` is not in the SDK container; **Codex** is (logged in with the hackathon key). Lanes run on Codex.
- After any Colima restart the container cannot reach the board: VM `lo` gets `192.168.1.10/24`; it must be `/32` (see setup.md in Senso).
- After re-plugging the board its IP is gone: `sudo nmcli connection up end0-static` over serial (`/dev/cu.usbserial-DK0JHTP8`, sima/edgeai).
- Stale `ffmpeg` / `watch_events.py` processes break the demo silently; the script kills them, but check if it "just stops".
- Every number is labelled measured / fixture / guessed. Never claim more than measured. Lean threshold 55 %/8 frames is a guess.

## Key paths
- Repo `~/workspace/watch` (main). Board app installed at `/home/sima/watch-perception/` on the board — re-`scp` after editing `perception/watch_events.py`.
- Lanes/board `~/workspace/watch-lanes/`; logs in `logs/`.
- Idea loop `~/Downloads/AI Infra Hackathon/self-improving idea experiment/` (MASTER, V1…, PROCESS) — each version frozen, pushed to Senso.
- Senso folder "AI Infra Hackathon" id `9882e827-371c-4451-942e-f7c56987d38e`.

## Standing preferences
- Aggressively token-prudent. Use `codex exec` for code and prose; Claude for board/serial, Chrome, merges, judgment.
- Clear context at task boundaries (after a submission, after a crucible round), after updating CURRENT.md in Senso with `kb patch-raw`. Compact proactively around 50–60 % context, not at the cliff.
- Two-failed-corrections rule: if the user has corrected the same thing twice, stop, write CURRENT.md, and suggest a clear.
- Progressive disclosure: never load setup.md, day1-summary, or the idea-loop versions wholesale; `senso search` the question, then `kb get-content` only the one document you need.
