#!/usr/bin/env python3
"""Dependency-free checks for ledger and trend helpers."""

from watch_events import (
    Pose,
    SitToStandDetector,
    TrendTracker,
    classify_posture,
    format_ledger_line,
    posture_measurements,
    read_nic,
    should_print,
)


def synthetic_pose(
    hip_y: float, shoulder_y: float, shoulder_x: float = 50.0,
    *, hips_visible: bool = True, nose_x: float = 50.0, nose_y: float = 10.0,
    bbox_aspect: float | None = None,
) -> Pose:
    points = [{"x": 0.0, "y": 0.0, "visibility": 0.0} for _ in range(17)]
    points[0] = {"x": nose_x, "y": nose_y, "visibility": 1.0}
    points[5] = {"x": shoulder_x - 5.0, "y": shoulder_y, "visibility": 1.0}
    points[6] = {"x": shoulder_x + 5.0, "y": shoulder_y, "visibility": 1.0}
    hip_visibility = 1.0 if hips_visible else 0.0
    points[11] = {"x": 45.0, "y": hip_y, "visibility": hip_visibility}
    points[12] = {"x": 55.0, "y": hip_y, "visibility": hip_visibility}
    return Pose(
        score=0.9, keypoints=points,
        bbox_w=None if bbox_aspect is None else bbox_aspect * 100,
        bbox_h=None if bbox_aspect is None else 100,
    )


def main() -> None:
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
    # Posture contract: absence means no pose, not merely missing torso keypoints.
    assert classify_posture([], 100, 100, 0.3) == "absent"
    assert classify_posture([
        synthetic_pose(0, 30, hips_visible=False, nose_x=50, nose_y=10)
    ], 100, 100, 0.3) == "upright"
    assert classify_posture([
        synthetic_pose(0, 30, hips_visible=False, nose_x=90, nose_y=30)
    ], 100, 100, 0.3) == "bent"
    assert classify_posture([synthetic_pose(50, 10)], 100, 100, 0.3) == "upright"
    assert classify_posture([synthetic_pose(80, 50)], 100, 100, 0.3) == "sitting"
    floor_tracker = TrendTracker()
    floor_pose = synthetic_pose(90, 70, bbox_aspect=1.4)
    assert floor_tracker.update([floor_pose], 100, 100, 0.3, 1.0) != "floor"
    assert floor_tracker.update([floor_pose], 100, 100, 0.3, 1.0) == "floor"
    assert floor_tracker.snapshot()["vis"] == "hips"
    assert floor_tracker.snapshot()["bbox_ar"] == 1.4
    shoulder_floor = TrendTracker()
    shoulder_pose = synthetic_pose(0, 90, hips_visible=False, bbox_aspect=1.4)
    assert shoulder_floor.update([shoulder_pose], 100, 100, 0.3, 1.0) != "floor"
    assert shoulder_floor.update([shoulder_pose], 100, 100, 0.3, 1.0) == "floor"
    seated_tracker = TrendTracker()
    seated_pose = synthetic_pose(0, 69, hips_visible=False, bbox_aspect=1.57)
    for _ in range(3):
        seated_tracker.update([seated_pose], 100, 100, 0.3, 1.0)
    assert seated_tracker.snapshot()["posture"] == "sitting"
    standing_pose = synthetic_pose(55, 37, bbox_aspect=1.0)
    assert seated_tracker.update([standing_pose], 100, 100, 0.3, 1.0) == "upright"
    assert seated_tracker.snapshot()["sts_n"] == 1
    assert isinstance(seated_tracker.snapshot()["sts_last_s"], float)
    close_standing = TrendTracker()
    for _ in range(2):
        close_standing.update([standing_pose], 100, 100, 0.3, 1.0)
    assert close_standing.snapshot()["posture"] == "upright"

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
