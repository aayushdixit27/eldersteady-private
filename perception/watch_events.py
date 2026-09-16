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
from math import atan2, degrees
from pathlib import Path
from typing import Iterable, Sequence


DEFAULT_DET_MODEL = Path("/workspace/models/yolo26m-det-int8-b1.tar.gz")
DEFAULT_POSE_MODEL = Path("/workspace/models/yolo26m-pose-int8-b1.tar.gz")
DEFAULT_VIDEO = Path("/workspace/assets/videos/video01.mp4")
SESSION_LEDGER = Path(__file__).with_name("session-ledger.json")
EVENT_STDOUT = None
COCO_LEFT_SHOULDER = 5
COCO_RIGHT_SHOULDER = 6
COCO_LEFT_HIP = 11
COCO_RIGHT_HIP = 12


@dataclass(frozen=True)
class Detection:
    x: int
    y: int
    w: int
    h: int
    score: float
    class_id: int


@dataclass(frozen=True)
class Pose:
    score: float
    keypoints: Sequence[dict[str, float]]


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


def write_session_ledger(
    path: Path,
    frames_processed: int,
    frames_in_events: int,
    events_emitted: int,
    frames_stored: int = 0,
    frames_uploaded: int = 0,
) -> dict:
    frames_unattributed = frames_processed - frames_in_events
    ledger = {
        "frames_processed": frames_processed,
        "frames_in_events": frames_in_events,
        "frames_unattributed": frames_unattributed,
        "events_emitted": events_emitted,
        "frames_stored": frames_stored,
        "frames_uploaded": frames_uploaded,
    }
    if frames_processed != frames_in_events + frames_unattributed:
        raise AssertionError("session ledger frame counts do not add up")
    path.write_text(json.dumps(ledger, separators=(",", ":")) + "\n", encoding="utf-8")
    return ledger


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", type=Path, default=None)
    parser.add_argument("--pose", action="store_true", help="run YOLO26 pose and emit fall events from torso lean")
    parser.add_argument("--video", type=str, default=str(DEFAULT_VIDEO))
    parser.add_argument("--room", default="living_room")
    parser.add_argument("--event-type", choices=("fall", "wander", "stove_unattended"), default="wander")
    parser.add_argument("--score-threshold", type=float, default=0.25)
    parser.add_argument("--nms-iou", type=float, default=0.60)
    parser.add_argument("--top-k", type=int, default=50)
    parser.add_argument("--max-frames", type=int, default=24)
    parser.add_argument("--stride", type=int, default=8)
    parser.add_argument("--timeout-ms", type=int, default=20000)
    parser.add_argument("--event-after-detections", type=int, default=1)
    parser.add_argument("--fall-lean-threshold", type=float, default=60.0)
    parser.add_argument("--fall-consecutive-frames", type=int, default=10)
    parser.add_argument("--min-keypoint-visibility", type=float, default=0.30)
    parser.add_argument("--host-ts", default=os.environ.get("WATCH_EVENT_TS", ""))
    parser.add_argument("--insight-host", default="")
    parser.add_argument("--insight-metadata-port", type=int, default=9100)
    args = parser.parse_args(argv[1:])
    if args.model is None:
        args.model = DEFAULT_POSE_MODEL if args.pose else DEFAULT_DET_MODEL
    elif not args.pose and "pose" in args.model.name:
        args.pose = True
    if args.pose:
        args.event_type = "fall"
    return args


def validate_args(args: argparse.Namespace) -> None:
    if not args.model.is_file():
        raise FileNotFoundError(f"model does not exist: {args.model}")
    if "://" not in args.video and not Path(args.video).is_file():
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
    if not 0.0 <= args.fall_lean_threshold <= 100.0:
        raise ValueError("--fall-lean-threshold must be in [0, 100]")
    if args.fall_consecutive_frames < 1:
        raise ValueError("--fall-consecutive-frames must be >= 1")
    if not 0.0 <= args.min_keypoint_visibility <= 1.0:
        raise ValueError("--min-keypoint-visibility must be in [0, 1]")


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


def tensor_to_numpy(tensor) -> object:
    shape = tuple(getattr(tensor, "shape", ()) or ())
    if not shape or 0 in shape:
        import numpy as np

        return np.empty(shape or (0,), dtype=np.float32)
    return tensor.to_numpy(copy=True)


def output_tensors(outputs) -> list[object]:
    if outputs is None:
        return []
    if isinstance(outputs, (list, tuple)):
        return list(outputs)
    if hasattr(outputs, "kind"):
        import pyneat

        if outputs.kind == pyneat.SampleKind.Tensor and outputs.tensor is not None:
            return [outputs.tensor]
        if outputs.kind == pyneat.SampleKind.TensorSet:
            return list(outputs.tensors)
        tensors = []
        for field in outputs.fields:
            tensors.extend(output_tensors(field))
        return tensors
    return [outputs]


def decode_pose_payload(outputs, frame_w: int, frame_h: int, max_poses: int) -> list[Pose]:
    import pyneat

    poses: list[Pose] = []
    decoded = pyneat.decode_pose(output_tensors(outputs), clamp_to=(frame_w, frame_h), top_k=max_poses)
    for item in decoded:
        boxes = tensor_to_numpy(item.boxes).reshape((-1, 6))
        keypoints = tensor_to_numpy(item.keypoints).reshape((-1, 17, 3))
        if boxes.shape[0] != keypoints.shape[0]:
            raise RuntimeError(
                f"pose decode returned {boxes.shape[0]} boxes but {keypoints.shape[0]} keypoint sets"
            )
        for box, points in zip(boxes, keypoints):
            if len(poses) >= max_poses:
                return poses
            poses.append(
                Pose(
                    score=float(box[4]),
                    keypoints=[
                        {"x": float(x), "y": float(y), "visibility": float(v)}
                        for x, y, v in points
                    ],
                )
            )
    return poses


def midpoint(a: dict[str, float], b: dict[str, float]) -> tuple[float, float]:
    return (a["x"] + b["x"]) / 2.0, (a["y"] + b["y"]) / 2.0


def torso_lean_percent(pose: Pose, min_visibility: float) -> float | None:
    keypoints = pose.keypoints
    required = (
        keypoints[COCO_LEFT_SHOULDER],
        keypoints[COCO_RIGHT_SHOULDER],
        keypoints[COCO_LEFT_HIP],
        keypoints[COCO_RIGHT_HIP],
    )
    if os.environ.get("WATCH_DEBUG_KP"):
        print("KP " + " ".join(f"{n}=({int(k['x'])},{int(k['y'])},v{k['visibility']:.2f})" for n, k in zip(("LS","RS","LH","RH"), required)), file=sys.stderr)
    if any(point["visibility"] < min_visibility for point in required):
        return None

    shoulder_x, shoulder_y = midpoint(keypoints[COCO_LEFT_SHOULDER], keypoints[COCO_RIGHT_SHOULDER])
    hip_x, hip_y = midpoint(keypoints[COCO_LEFT_HIP], keypoints[COCO_RIGHT_HIP])
    dx = shoulder_x - hip_x
    dy = shoulder_y - hip_y
    if dx == 0.0 and dy == 0.0:
        return None
    angle = degrees(atan2(abs(dx), abs(dy)))
    return max(0.0, min(100.0, (angle / 90.0) * 100.0))


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
    opt.decode_type = pyneat.BoxDecodeType.YoloV26Pose if args.pose else pyneat.BoxDecodeType.YoloV26
    if args.pose:
        opt.num_classes = 1
    opt.score_threshold = args.score_threshold
    opt.nms_iou_threshold = args.nms_iou
    opt.top_k = args.top_k
    model = pyneat.Model(str(args.model), opt)

    cap = cv2.VideoCapture(str(args.video), cv2.CAP_FFMPEG) if "://" in str(args.video) else cv2.VideoCapture(str(args.video))
    tries = 0
    while not cap.isOpened() and "://" in str(args.video) and tries < 10:
        tries += 1
        print(f"waiting for stream {args.video} ({tries}/10)", file=sys.stderr)
        time.sleep(2)
        cap = cv2.VideoCapture(str(args.video), cv2.CAP_FFMPEG) if "://" in str(args.video) else cv2.VideoCapture(str(args.video))
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
    frames_in_events = 0
    events_emitted = 0
    frames_with_detections = 0
    event_emitted = False
    frame_index = 0
    bent_streak = 0

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
            processed += 1
            frames_since_event += 1

            if args.pose:
                poses = decode_pose_payload(outputs, frame.shape[1], frame.shape[0], args.top_k)
                lean_values = [
                    lean
                    for pose in poses
                    if (lean := torso_lean_percent(pose, args.min_keypoint_visibility)) is not None
                ]
                best_lean = max(lean_values, default=0.0)
                best_score = max((pose.score for pose in poses), default=0.0)
                is_bent = best_lean >= args.fall_lean_threshold
                bent_streak = bent_streak + 1 if is_bent else 0
                posture = "BENT" if is_bent else "upright"
                log(
                    "frame={} processed={} posture={} lean={:.0f}% poses={} valid_lean={} best={:.3f} bent_streak={} infer_ms={:.1f}".format(
                        frame_index,
                        processed,
                        posture,
                        best_lean,
                        len(poses),
                        len(lean_values),
                        best_score,
                        bent_streak,
                        elapsed_ms,
                    )
                )
                if not event_emitted and bent_streak >= args.fall_consecutive_frames:
                    event = {
                        "type": "fall",
                        "room": args.room,
                        "ts": event_timestamp(args.host_ts),
                        "confidence": round(best_score, 3),
                        "discarded_frames": frames_since_event,
                    }
                    emit_event(event)
                    event_emitted = True
                    frames_in_events += frames_since_event
                    events_emitted += 1
                    frames_since_event = 0
            else:
                detections = parse_bbox_payload(bbox_payload(outputs), args.score_threshold)
                send_insight_metadata(args.insight_host, args.insight_metadata_port, frame_index, detections)
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
                    frames_in_events += frames_since_event
                    events_emitted += 1
                    frames_since_event = 0

        ledger = write_session_ledger(
            SESSION_LEDGER,
            frames_processed=processed,
            frames_in_events=frames_in_events,
            events_emitted=events_emitted,
        )
        log(f"done processed={processed} event_emitted={event_emitted} ledger={SESSION_LEDGER} {ledger}")
        if event_emitted or (args.pose and processed > 0):
            return 0
        return 3
    finally:
        cap.release()
        runner.close()


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv))
    except Exception as exc:
        log(f"error: {exc}")
        raise SystemExit(2)
