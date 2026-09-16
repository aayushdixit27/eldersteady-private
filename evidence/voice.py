#!/usr/bin/env python3
"""Offline, short-lived voice check after a fall event."""

from __future__ import annotations

import argparse
import json
import queue
import sys
import time
from pathlib import Path
from typing import Callable


GRAMMAR = ["help", "i have fallen", "i am okay", "i'm okay", "okay", "[unk]"]
MODEL_DIR = Path(__file__).with_name("models") / "vosk-model-small-en-us-0.15"
RECORD_AUDIO = False
# Privacy invariant: this program has no recording/output-audio path.
assert RECORD_AUDIO is False


def phrase_to_keyword(text: str) -> str:
    """Map a recognizer phrase to the board's small response vocabulary."""
    phrase = " ".join(text.lower().strip().split())
    if phrase == "help":
        return "help"
    if phrase == "i have fallen":
        return "fallen"
    if phrase in {"i am okay", "i'm okay", "okay"}:
        return "okay"
    return "none"


def format_board_line(keyword: str, heard_s: float, text: str | None) -> str:
    """Return the single-line, safely quoted voice result."""
    clean = " ".join((text or "none").split()) or "none"
    quoted = json.dumps(clean, ensure_ascii=True)
    return f"voice keyword={keyword} heard_s={heard_s:.1f} recorded_s=0 text={quoted}"


def _recognizer_text(result: str) -> str:
    try:
        return str(json.loads(result).get("text", "")).strip()
    except (json.JSONDecodeError, AttributeError):
        return ""


class MicrophoneError(RuntimeError):
    pass


def listen(model_dir: Path, window: float, on_phrase: Callable[[str], None] | None = None) -> tuple[str, str, float]:
    """Listen from the default microphone; samples exist only in memory."""
    import sounddevice as sd
    from vosk import KaldiRecognizer, Model

    audio: queue.Queue[bytes] = queue.Queue()
    recognizer = KaldiRecognizer(Model(str(model_dir)), 16000, json.dumps(GRAMMAR))
    started = time.monotonic()
    phrases: list[str] = []

    def callback(indata, frames, timing, status) -> None:  # sounddevice callback signature
        del frames, timing, status
        audio.put(bytes(indata))

    try:
        # RawInputStream is input-only; no audio file or output stream is opened.
        with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype="int16", channels=1, callback=callback):
            while time.monotonic() - started < window:
                remaining = window - (time.monotonic() - started)
                try:
                    chunk = audio.get(timeout=max(0.01, min(0.25, remaining)))
                except queue.Empty:
                    continue
                if recognizer.AcceptWaveform(chunk):
                    text = _recognizer_text(recognizer.Result())
                    if text:
                        phrases.append(text)
                        if on_phrase:
                            on_phrase(text)
    except Exception as exc:
        raise MicrophoneError(f"cannot open the default microphone (check microphone permission): {exc}") from exc

    final = _recognizer_text(recognizer.FinalResult())
    if final:
        phrases.append(final)
        if on_phrase:
            on_phrase(final)
    elapsed = time.monotonic() - started
    best = next((phrase for phrase in phrases if phrase_to_keyword(phrase) in {"help", "fallen"}), None)
    best = best or next((phrase for phrase in phrases if phrase_to_keyword(phrase) == "okay"), None)
    return phrase_to_keyword(best or ""), best or "none", elapsed


def is_fall_line(line: str) -> bool:
    try:
        event = json.loads(line)
    except (json.JSONDecodeError, TypeError):
        return False
    return isinstance(event, dict) and event.get("type") == "fall"


def watch(log_path: Path, model_dir: Path, window: float) -> int:
    offset = log_path.stat().st_size if log_path.exists() else 0
    pending = ""
    while True:
        try:
            size = log_path.stat().st_size
            if size < offset:
                offset, pending = 0, ""
            if size > offset:
                with log_path.open("r", errors="replace") as stream:
                    stream.seek(offset)
                    data = stream.read()
                    offset = stream.tell()
                lines = (pending + data).splitlines(keepends=True)
                pending = ""
                if lines and not lines[-1].endswith(("\n", "\r")):
                    pending = lines.pop()
                for line in lines:
                    if is_fall_line(line):
                        keyword, text, elapsed = listen(model_dir, window)
                        result = format_board_line(keyword, elapsed, text)
                        with log_path.open("a") as stream:
                            stream.write(result + "\n")
                        offset = log_path.stat().st_size
        except FileNotFoundError:
            offset, pending = 0, ""
        time.sleep(0.2)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--log", type=Path, required=True)
    parser.add_argument("--window", type=float)
    parser.add_argument("--test", action="store_true")
    args = parser.parse_args()
    window = args.window if args.window is not None else (10.0 if args.test else 60.0)
    if window <= 0:
        parser.error("--window must be greater than zero")
    if not MODEL_DIR.is_dir():
        print(f"voice: Vosk model directory not found: {MODEL_DIR}", file=sys.stderr)
        return 2
    try:
        if args.test:
            keyword, _text, _elapsed = listen(MODEL_DIR, window, lambda text: print(f"heard: {text}", flush=True))
            print(f"RESULT keyword={keyword}")
            return 0
        return watch(args.log, MODEL_DIR, window)
    except MicrophoneError as exc:
        print(f"voice: {exc}", file=sys.stderr)
        return 2
    except (ImportError, OSError) as exc:
        print(f"voice: offline speech setup unavailable: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
