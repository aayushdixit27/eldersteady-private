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
) -> Pose:
    points = [{"x": 0.0, "y": 0.0, "visibility": 0.0} for _ in range(17)]
    points[0] = {"x": nose_x, "y": nose_y, "visibility": 1.0}
    points[5] = {"x": shoulder_x - 5.0, "y": shoulder_y, "visibility": 1.0}
    points[6] = {"x": shoulder_x + 5.0, "y": shoulder_y, "visibility": 1.0}
    hip_visibility = 1.0 if hips_visible else 0.0
    points[11] = {"x": 45.0, "y": hip_y, "visibility": hip_visibility}
    points[12] = {"x": 55.0, "y": hip_y, "visibility": hip_visibility}
    return Pose(score=0.9, keypoints=points)


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
    floor_pose = synthetic_pose(92, 86)
    assert floor_tracker.update([floor_pose], 100, 100, 0.3, 1.0) != "floor"
    assert floor_tracker.update([floor_pose], 100, 100, 0.3, 1.0) == "floor"
    assert floor_tracker.snapshot()["vis"] == "hips"

    detector = SitToStandDetector()
    for pose, now in (
        (synthetic_pose(75, 50), 2.0),
        (synthetic_pose(72, 47), 3.0),
        (synthetic_pose(55, 30), 5.5),
    ):
        hip_y, _, upright, _ = posture_measurements(pose, 100, 100, 0.3)
        detector.update(hip_y, upright, now)
    assert detector.count == 1 and detector.last_duration == 3.5
    for pose, now in ((synthetic_pose(75, 50), 10.0), (synthetic_pose(55, 30), 21.0)):
        hip_y, _, upright, _ = posture_measurements(pose, 100, 100, 0.3)
        detector.update(hip_y, upright, now)
    assert detector.count == 1
    print("test_ledger: posture and ledger checks passed")


if __name__ == "__main__":
    main()
