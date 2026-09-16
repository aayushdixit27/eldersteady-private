# Offline post-fall voice check
Run `python3 -m evidence.voice --log interface/live/board.log` to watch for new falls.
After each fall it listens to the default Mac microphone for 60 seconds.
Use `--window SECONDS` to change that interval.
Use `--test` for an immediate 10-second live phrase check; it prints heard phrases and the result.
Download the small English Vosk model into `evidence/models/vosk-model-small-en-us-0.15` first.
Allow microphone access for Terminal in macOS System Settings if opening the mic fails.
audio is processed on the laptop in the room today; on the MLA is roadmap; nothing is recorded
