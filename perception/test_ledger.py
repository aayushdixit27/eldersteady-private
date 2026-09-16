#!/usr/bin/env python3
"""Dependency-free checks for the NIC/pixel ledger helpers."""

from watch_events import format_ledger_line, read_nic, should_print


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
    print("test_ledger: 4 checks passed")


if __name__ == "__main__":
    main()
