"""Validation utilities for OpenModelica simulation time parameters."""

from __future__ import annotations


def validate_time_range(
    start_time: int, stop_time: int, max_stop_exclusive: int = 5
) -> tuple[bool, str]:
    """Validate simulation start/stop time constraints.

    Enforces: 0 <= start_time < stop_time < max_stop_exclusive

    Args:
        start_time: Simulation start time.
        stop_time: Simulation stop time.
        max_stop_exclusive: Exclusive upper bound for stop_time (default 5,
            per the screening task specification).

    Returns:
        A tuple ``(is_valid, message)``. ``message`` is empty when
        ``is_valid`` is True, otherwise it explains which constraint failed.
    """
    if start_time < 0:
        return False, "Start time must be greater than or equal to 0."
    if not start_time < stop_time:
        return False, "Start time must be strictly less than stop time."
    if not stop_time < max_stop_exclusive:
        return False, f"Stop time must be strictly less than {max_stop_exclusive}."
    return True, ""
