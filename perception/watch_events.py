#!/usr/bin/env python3
"""Emit watch.event JSONL from YOLO26 detections on a video file."""

from __future__ import annotations

import argparse
import json
import os
import socket
import struct
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


DEFAULT_MODEL = Path("/workspace/models/yolo26m-det-int8-b1.tar.gz")
DEFAULT_VIDEO = Path("/workspace/assets/videos/video01.mp4")
EVENT_STDOUT = None


@dataclass(frozen=True)
class Detection:
    x: int
    y: int
    w: int
    h: int
    score: float
    class_id: int


def log(message: str) -> None:
    print(message, file=sys.stderr, flush=True)


def reserve_event_stdout() -> None:
    global EVENT_STDOUT
    if EVENT_STDOUT is not None:
        return
    EVENT_STDOUT = os.fdopen(os.dup(sys.stdout.fileno()), "w", buffering=1)
    os.dup2(sys.stderr.fileno(), sys.stdout.fileno())


def emit_event(event: dict) -> None:
    if EVENT_STDOUT is None:
        print(json.dumps(event, separators=(",", ":")), flush=True)
        return
    print(json.dumps(event, separators=(",", ":")), file=EVENT_STDOUT, flush=True)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", type=Path, default=DEFAULT_MODEL)
    parser.add_argument("--video", type=Path, default=DEFAULT_VIDEO)
    parser.add_argument("--room", default="living_room")
    parser.add_argument("--event-type", choices=("fall", "wander", "stove_unattended"), default="wander")
    parser.add_argument("--score-threshold", type=float, default=0.25)
    parser.add_argument("--nms-iou", type=float, default=0.60)
    parser.add_argument("--top-k", type=int, default=50)
    parser.add_argument("--max-frames", type=int, default=24)
    parser.add_argument("--stride", type=int, default=8)
    parser.add_argument("--timeout-ms", type=int, default=20000)
    parser.add_argument("--event-after-detections", type=int, default=1)
    parser.add_argument("--host-ts", default=os.environ.get("WATCH_EVENT_TS", ""))
    parser.add_argument("--insight-host", default="")
    parser.add_argument("--insight-metadata-port", type=int, default=9100)
    return parser.parse_args(argv[1:])


def validate_args(args: argparse.Namespace) -> None:
    if not args.model.is_file():
        raise FileNotFoundError(f"model does not exist: {args.model}")
    if not args.video.is_file():
        raise FileNotFoundError(f"video does not exist: {args.video}")
    if not 0.0 <= args.score_threshold <= 1.0:
        raise ValueError("--score-threshold must be in [0, 1]")
    if not 0.0 <= args.nms_iou <= 1.0:
        raise ValueError("--nms-iou must be in [0, 1]")
    if args.top_k < 1:
        raise ValueError("--top-k must be >= 1")
    if args.max_frames < 1:
        raise ValueError("--max-frames must be >= 1")
    if args.stride < 1:
        raise ValueError("--stride must be >= 1")
    if args.event_after_detections < 1:
        raise ValueError("--event-after-detections must be >= 1")


def event_timestamp(host_ts: str) -> str:
    if host_ts:
        if not host_ts.endswith("Z"):
            raise ValueError("--host-ts must be UTC and Z-suffixed")
        return host_ts
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def bbox_payload(tensors: Iterable[object]) -> bytes:
    tensors = list(tensors)
    if len(tensors) != 1:
        return b""
    tensor = tensors[0]
    if hasattr(tensor, "copy_payload_bytes"):
        return bytes(tensor.copy_payload_bytes())
    if hasattr(tensor, "to_numpy"):
        return bytes(tensor.to_numpy(copy=False))
    return b""


def parse_bbox_payload(payload: bytes, min_score: float) -> list[Detection]:
    if len(payload) < 4:
        return []
    count = min(struct.unpack_from("<I", payload, 0)[0], (len(payload) - 4) // 24)
    detections: list[Detection] = []
    offset = 4
    for _ in range(count):
        x, y, w, h, score, class_id = struct.unpack_from("<iiiifi", payload, offset)
        offset += 24
        if w <= 0 or h <= 0 or score < min_score:
            continue
        detections.append(Detection(x=x, y=y, w=w, h=h, score=float(score), class_id=int(class_id)))
    return detections


def send_insight_metadata(host: str, port: int, frame_id: int, detections: list[Detection]) -> None:
    if not host:
        return
    objects = [
        {
            "id": f"det_{frame_id}_{index}",
            "label": str(det.class_id),
            "confidence": round(det.score, 3),
            "bbox": [int(det.x), int(det.y), int(det.w), int(det.h)],
        }
        for index, det in enumerate(detections, start=1)
    ]
    payload = {
        "type": "object-detection",
        "timestamp": int(time.monotonic() * 1000),
        "frame_id": frame_id,
        "data": {"objects": objects},
    }
    packet = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.sendto(packet, (host, port))
    finally:
        sock.close()


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    validate_args(args)
    reserve_event_stdout()

    import cv2
    import numpy as np
    import pyneat

    log(f"loading model={args.model}")
    opt = pyneat.ModelOptions()
    opt.preprocess.kind = pyneat.InputKind.Image
    opt.preprocess.enable = pyneat.AutoFlag.On
    opt.preprocess.color_convert.input_format = pyneat.PreprocessColorFormat.BGR
    opt.preprocess.preset = pyneat.NormalizePreset.COCO_YOLO
    opt.decode_type = pyneat.BoxDecodeType.YoloV26
    opt.score_threshold = args.score_threshold
    opt.nms_iou_threshold = args.nms_iou
    opt.top_k = args.top_k
    model = pyneat.Model(str(args.model), opt)

    cap = cv2.VideoCapture(str(args.video))
    if not cap.isOpened():
        raise RuntimeError(f"failed to open video: {args.video}")

    ok, first = cap.read()
    if not ok or first is None:
        raise RuntimeError(f"failed to read first frame: {args.video}")

    first = np.ascontiguousarray(first, dtype=np.uint8)
    seed = pyneat.Tensor.from_numpy(
        first,
        copy=True,
        image_format=pyneat.PixelFormat.BGR,
        memory=pyneat.TensorMemory.EV74,
    )
    run_opt = pyneat.RunOptions()
    run_opt.queue_depth = 4
    run_opt.overflow_policy = pyneat.OverflowPolicy.Block
    run_opt.preset = pyneat.RunPreset.Balanced
    runner = model.build([seed], route_options=pyneat.ModelRouteOptions(), run_options=run_opt)

    processed = 0
    frames_since_event = 0
    frames_with_detections = 0
    event_emitted = False
    frame_index = 0

    try:
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        while processed < args.max_frames:
            ok, frame = cap.read()
            if not ok or frame is None:
                break
            frame_index += 1
            if (frame_index - 1) % args.stride != 0:
                continue

            tensor = pyneat.Tensor.from_numpy(
                np.ascontiguousarray(frame, dtype=np.uint8),
                copy=True,
                image_format=pyneat.PixelFormat.BGR,
                memory=pyneat.TensorMemory.EV74,
            )
            started = time.perf_counter()
            outputs = runner.run([tensor], timeout_ms=args.timeout_ms)
            elapsed_ms = (time.perf_counter() - started) * 1000.0
            detections = parse_bbox_payload(bbox_payload(outputs), args.score_threshold)
            send_insight_metadata(args.insight_host, args.insight_metadata_port, frame_index, detections)

            processed += 1
            frames_since_event += 1
            if detections:
                frames_with_detections += 1
            best = max((det.score for det in detections), default=0.0)
            log(
                "frame={} processed={} detections={} best={:.3f} infer_ms={:.1f}".format(
                    frame_index, processed, len(detections), best, elapsed_ms
                )
            )

            if (
                detections
                and not event_emitted
                and frames_with_detections >= args.event_after_detections
            ):
                event = {
                    "type": args.event_type,
                    "room": args.room,
                    "ts": event_timestamp(args.host_ts),
                    "confidence": round(best, 3),
                    "discarded_frames": frames_since_event,
                }
                emit_event(event)
                event_emitted = True
                frames_since_event = 0

        log(f"done processed={processed} event_emitted={event_emitted}")
        return 0 if event_emitted else 3
    finally:
        cap.release()
        runner.close()


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv))
    except Exception as exc:
        log(f"error: {exc}")
        raise SystemExit(2)
