# How ElderSteady Private used Senso

*16 September 2026. Written for the Senso team by the setup lane, from the folder's own record.*

## The shape of the problem

One founder, one board, and — by mid-morning on day 2 — **six agents**: three Claude Code sessions, one Codex/GPT-6 research lane, Codex build lanes under the setup session, and an architect session from day 1. Every one of them starts with amnesia. The failure that kills hackathon teams is not lack of speed; it is six workers with six different pictures of what is true.

## What we did

**One folder, "AI Infra Hackathon", was the team's memory. 20 documents by 10:50 on day 2.**

1. **A progress file, revised in place.** `watch/CURRENT.md` — task, state, settled decisions, rejected alternatives, next action — patched with `senso kb patch-raw` at every task boundary (rev 4 today). A fresh session reads it first: ~2.5k tokens to be fully oriented. The root instruction file (`CLAUDE.md`) is 45 lines and says: fetch CURRENT.md, then ask Senso before reading the repo.
2. **Questions go to Senso before they go to a person.** `senso search "<question>"` returned an answer plus source node ids; `kb get-content <id>` only when the full document was needed. Example: "how do I bring the board back after a re-plug" → `setup.md` §6 → `nmcli connection up end0-static`, without loading the runbook wholesale.
3. **Lanes hand work to each other by node id.** Research briefs, catch-ups and outlines were pushed with `kb create-raw`; the receiving lane was told the id. The research lane (a different vendor's model, no repo access) read its brief from Senso and wrote its findings back — `research/round-3.md`, `round-4-wording.md`, `copy-deck-and-objections.md` — which the UI and pitch lanes then pulled. No copy-paste of documents between agents.
4. **A self-improving idea loop with every version frozen.** MASTER, V1…V4, PROCESS (rev 5), killerideas — each crucible round wrote a new version and pushed it; any lane can see why an idea was parked and what would revive it.
5. **Provenance survives hand-offs.** Because documents carry their labels (measured / fixture / guessed), a lane that pulled numbers from Senso pulled the labels with them; the README and pitch inherited them without re-litigation.

## What it caught

- A search for the judging rubric returned a confident "four × 25 %, GPT-6 Astra in development and in product" — sourced from **a different hackathon's documents** in the same organisation. Because the answer came with node ids, the source was checked in two calls and the rubric was discarded before it shaped the README. Lesson for the product: scope search to a folder by default, or show the folder on every source.
- The handoff verifier (a fresh agent given only the handoff) found one claim the runbook did not support; the runbook was patched (setup.md rev 2) before day 2 started.

## The value, plainly

- **Cold start cost:** CLAUDE.md + CURRENT.md ≈ 3.5k tokens, versus re-reading a repo and a day of transcripts.
- **Six agents, one truth:** every lane's identity check ("LANE / WHO / OWN / BRANCH / NOW") resolved against the same progress file; the one collision we had (two lanes on one branch) was a labelling slip, caught in minutes because the roster lived in one place.
- **Research is a lane, not a chore:** three research rounds (regulation, DevKit outputs, prior art; plain-language wording for older adults; hostile-persona review of the pitch) ran in parallel with building, each 15–25 minutes, each written back where the next reader would look.
- **The decisions have their reasons attached** — rulings, rejected alternatives, and the graveyard of parked ideas — so nobody proposed Docker Desktop or a cloud deploy twice.

## Commands that did the work

```
senso kb get-content <node> --output json --quiet      # read one document
senso search "<question in plain words>" --output json --quiet
senso kb create-raw --data '{"text":…,"title":…,"kb_folder_node_id":…}'
senso kb patch-raw <node> --data '{"text":…}'          # revise in place; --rev n keeps history
senso kb children <folder>                              # the roster of documents
```

## What we did not use

Tags, public sharing, evaluation/remediation and publishing flows — a hackathon needs memory and hand-off, not distribution. The one wish: a folder-scoped search flag, or the folder name on every returned source.
