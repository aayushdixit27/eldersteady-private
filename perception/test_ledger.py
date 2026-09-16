#!/usr/bin/env python3
"""Dependency-free checks for ledger and trend helpers."""

from unittest.mock import patch

from watch_events import (
    Detection,
    FallEventCooldown,
    Pose,
    SitToStandDetector,
    TrendTracker,
    classify_posture,
    dedupe_pose_boxes,
    event_timestamp,
    format_ledger_line,
    format_pose_frame_line,
    posture_measurements,
    pose_box_geometry,
    read_nic,
    should_print,
)


def synthetic_pose(
    hip_y: float, shoulder_y: float, shoulder_x: float = 50.0,
    *, hips_visible: bool = True, nose_x: float = 50.0, nose_y: float = 10.0,
    bbox_aspect: float | None = None, bbox_x: float = 0.0,
    bbox_y: float = 0.0,
    ankle_x: tuple[float, float] | None = None, score: float = 0.9,
    bbox_size: tuple[float, float] | None = None,
) -> Pose:
    points = [{"x": 0.0, "y": 0.0, "visibility": 0.0} for _ in range(17)]
    points[0] = {"x": nose_x, "y": nose_y, "visibility": 1.0}
    points[5] = {"x": shoulder_x - 5.0, "y": shoulder_y, "visibility": 1.0}
    points[6] = {"x": shoulder_x + 5.0, "y": shoulder_y, "visibility": 1.0}
    hip_visibility = 1.0 if hips_visible else 0.0
    points[11] = {"x": 45.0, "y": hip_y, "visibility": hip_visibility}
    points[12] = {"x": 55.0, "y": hip_y, "visibility": hip_visibility}
    if ankle_x is not None:
        points[15] = {"x": ankle_x[0], "y": 90.0, "visibility": 1.0}
        points[16] = {"x": ankle_x[1], "y": 90.0, "visibility": 1.0}
    return Pose(
        score=score, keypoints=points,
        bbox_w=bbox_size[0] if bbox_size else (None if bbox_aspect is None else bbox_aspect * 100),
        bbox_h=bbox_size[1] if bbox_size else (None if bbox_aspect is None else 100),
        bbox_x=bbox_x,
        bbox_y=bbox_y,
    )


def main() -> None:
    with patch("watch_events.time.monotonic", side_effect=(100.0, 105.0)):
        first = event_timestamp("2026-09-16T16:27:48Z", 100.0)
        second = event_timestamp("2026-09-16T16:27:48Z", 100.0)
    assert first == "2026-09-16T16:27:48Z"
    assert second == "2026-09-16T16:27:53Z"

    assert read_nic("watch-interface-that-does-not-exist") == (None, None)
    assert format_ledger_line(30, 186624000, 1200, 47) == (
        "ledger frames=30 pixel_bytes=186624000 rx_bytes=1200 tx_bytes=47 nic=end0"
    )
    assert format_ledger_line(0, 0, None, None) == (
        "ledger frames=0 pixel_bytes=0 rx_bytes=na tx_bytes=na nic=end0"
    )
    assert [should_print(frame, changed, streak, 5) for frame, changed, streak in (
        (1, False, 0), (5, False, 0), (6, True, 0), (7, False, 1)
    )] == [False, True, True, True]
    assert format_pose_frame_line(7, 4, "upright", 12, 1, 1, 0.875, 0, 8.25, "full") == (
        "frame=7 processed=4 posture=upright lean=12% poses=1 valid_lean=1 "
        "best=0.875 bent_streak=0 infer_ms=8.2 view=full"
    )
    assert format_pose_frame_line(
        10, 5, "sitting", 4, 1, 1, 0.9, 0, 8.25, "full", 6.75
    ).endswith("bent_streak=0 infer_ms=8.2 view=full det_ms=6.8")
    with patch.dict("watch_events.os.environ", {}, clear=True):
        assert pose_box_geometry((10, 20, 110, 220)) == (10, 20, 110, 220)
    with patch.dict("watch_events.os.environ", {"WATCH_BOX_XYXY": "1"}, clear=True):
        assert pose_box_geometry((10, 20, 110, 220)) == (10, 20, 100, 200)
    # Posture contract: absence means no pose, not merely missing torso keypoints.
    assert classify_posture([], 100, 100, 0.3) == "absent"
    assert classify_posture([
        synthetic_pose(0, 30, hips_visible=False, nose_x=50, nose_y=10)
    ], 100, 100, 0.3) == "upright"
    assert classify_posture([
        synthetic_pose(0, 30, hips_visible=False, nose_x=90, nose_y=30)
    ], 100, 100, 0.3) == "bent"
    assert classify_posture([synthetic_pose(55, 20, bbox_aspect=1.0)], 100, 100, 0.3) == "upright"
    assert classify_posture([synthetic_pose(66, 52, bbox_aspect=1.2)], 100, 100, 0.3) == "sitting"

    # Furniture detections are facts, independent of the calibrated shoulder band.
    chair_tracker = TrendTracker()
    chair_pose = synthetic_pose(70, 20, bbox_size=(30, 70), bbox_x=35, bbox_y=10)
    chair = Detection(35, 60, 30, 35, 0.9, 56)
    assert chair_tracker.update(
        [chair_pose], 100, 100, 0.3, 0.1, detections=[chair], det_ms=4.2
    ) == "sitting"
    assert chair_tracker.snapshot()["objects"] == "chair:1"
    assert chair_tracker.snapshot()["det_ms"] == 4.2
    chair_tracker.update([chair_pose], 100, 100, 0.3, 0.1)
    assert chair_tracker.snapshot()["det_ms"] == 4.2
    assert chair_tracker.snapshot()["floor_s"] == 0.0

    bed_tracker = TrendTracker()
    wide_pose = synthetic_pose(75, 75, bbox_size=(90, 45), bbox_x=5, bbox_y=50)
    bed = Detection(0, 45, 100, 55, 0.95, 59)
    assert bed_tracker.update(
        [wide_pose], 100, 100, 0.3, 2.0, detections=[bed], det_ms=5.0
    ) == "lying"
    assert bed_tracker.snapshot()["floor_s"] == 0.0
    shoulder_floor = TrendTracker()
    shoulder_pose = synthetic_pose(0, 75, hips_visible=False, bbox_aspect=1.5)
    assert shoulder_floor.update([shoulder_pose], 100, 100, 0.3, 0.5) == "close"
    assert shoulder_floor.update([shoulder_pose], 100, 100, 0.3, 0.5) == "close"
    assert shoulder_floor.update([shoulder_pose], 100, 100, 0.3, 0.5) == "close"
    assert shoulder_floor.snapshot()["floor_s"] == 0.0
    assert shoulder_floor.snapshot()["view"] == "close"
    assert shoulder_floor.snapshot()["vis"] == "shoulders"
    assert shoulder_floor.snapshot()["bbox_ar"] == 1.5
    seated_tracker = TrendTracker()
    seated_pose = synthetic_pose(66, 52, bbox_aspect=1.2)
    for _ in range(2):
        seated_tracker.update([seated_pose], 100, 100, 0.3, 1.0)
    assert seated_tracker.snapshot()["posture"] == "sitting"
    standing_pose = synthetic_pose(55, 20, bbox_aspect=1.0)
    seated_tracker.update([standing_pose], 100, 100, 0.3, 0.01)
    assert seated_tracker.snapshot()["sts_n"] == 1
    assert seated_tracker.snapshot()["sts_last_s"] == 0.01
    close_standing = TrendTracker()
    for _ in range(2):
        close_standing.update([standing_pose], 100, 100, 0.3, 1.0)
    assert close_standing.snapshot()["posture"] == "upright"

    # The nearest (largest) person is the subject, regardless of pose score.
    far = synthetic_pose(55, 20, score=0.99, bbox_size=(20, 40))
    near = synthetic_pose(66, 52, score=0.51, bbox_size=(60, 80))
    nearest = TrendTracker()
    nearest.update([far, near], 100, 100, 0.3, 1.0)
    assert nearest.snapshot()["posture"] == "sitting"
    assert nearest.snapshot()["subject_area"] == 0.48
    assert nearest.snapshot()["company_s"] == 1.0
    assert nearest.snapshot()["subject"] == "clear"

    # Overlapping detections of one person count once; a distant person remains.
    duplicate = synthetic_pose(66, 52, score=0.95, bbox_size=(60, 80), bbox_x=6.67)
    distant = synthetic_pose(55, 20, bbox_size=(10, 20), bbox_x=85)
    deduped = dedupe_pose_boxes([near, duplicate, distant])
    assert len(deduped) == 2
    deduped_tracker = TrendTracker()
    deduped_tracker.update(deduped, 100, 100, 0.3, 1.0)
    assert deduped_tracker.snapshot()["subject"] == "clear"

    # Similar-size people are ambiguous; stable dominance must persist before
    # posture logic resumes for a newly clear subject.
    ambiguous = TrendTracker()
    peer = synthetic_pose(55, 20, bbox_size=(58, 80))
    assert ambiguous.update([near, peer], 100, 100, 0.3, 0.1) == "unclear"
    assert ambiguous.snapshot()["view"] == "unclear"
    assert ambiguous.snapshot()["subject"] == "unclear"
    assert ambiguous.snapshot()["company_s"] == 0.1
    for _ in range(4):
        ambiguous.update([near, far], 100, 100, 0.3, 0.1)
    assert ambiguous.snapshot()["subject"] == "unclear"
    ambiguous.update([near, far], 100, 100, 0.3, 0.1)
    assert ambiguous.snapshot()["subject"] == "clear"

    floor_flicker = TrendTracker()
    floor_pose = synthetic_pose(75, 75, bbox_aspect=1.5)
    floor_flicker.update([floor_pose], 100, 100, 0.3, 1.0)
    floor_flicker.update([standing_pose], 100, 100, 0.3, 0.1)
    assert floor_flicker.snapshot()["floor_s"] == 1.0
    assert floor_flicker.update([floor_pose], 100, 100, 0.3, 0.5) == "floor"

    walking = TrendTracker()
    # 17 alternating signs in ten seconds gives 100-ish steps/minute.
    for index in range(18):
        left_first = index % 2 == 0
        walking.update([synthetic_pose(
            55, 20, shoulder_x=50 + index * 0.05, bbox_aspect=0.5,
            bbox_x=index * 0.4, ankle_x=(40, 60) if left_first else (60, 40),
        )], 100, 100, 0.3, 10 / 17)
    assert 96 <= walking.snapshot()["cadence_spm"] <= 102

    still = TrendTracker()
    for index in range(20):
        still.update([synthetic_pose(
            55, 20, shoulder_x=50 + (0.1 if index % 2 else -0.1),
            bbox_aspect=0.5, bbox_x=20,
        )], 100, 100, 0.3, 0.25)
    assert still.snapshot()["sway"] < 0.01

    cooldown = FallEventCooldown()
    assert cooldown.ready(0.0)
    cooldown.emitted(0.0)
    cooldown.update("upright", 21.0)
    cooldown.update("upright", 23.0)
    assert cooldown.ready(25.0)
    cooldown.emitted(25.0)
    assert not cooldown.ready(25.0)

    detector = SitToStandDetector()
    for pose, now in ((synthetic_pose(75, 50), 0.0), (synthetic_pose(75, 50), 2.0),
                      (synthetic_pose(55, 30), 3.0)):
        hip_y, _, upright, _ = posture_measurements(pose, 100, 100, 0.3)
        detector.update(hip_y, upright, now)
    assert detector.count == 1 and detector.last_duration == 1.0
    flap = SitToStandDetector()
    for index in range(20):
        pose = synthetic_pose(75 if index % 2 == 0 else 55, 50 if index % 2 == 0 else 30)
        hip_y, _, upright, _ = posture_measurements(pose, 100, 100, 0.3)
        flap.update(hip_y, upright, index * 0.033)
    assert flap.count == 0
    for pose, now in ((synthetic_pose(75, 50), 10.0), (synthetic_pose(55, 30), 21.0)):
        hip_y, _, upright, _ = posture_measurements(pose, 100, 100, 0.3)
        detector.update(hip_y, upright, now)
    assert detector.count == 1
    print("test_ledger: posture and ledger checks passed")


if __name__ == "__main__":
    main()
