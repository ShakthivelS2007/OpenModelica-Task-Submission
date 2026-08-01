"""Unit tests for time-range validation logic (no Qt/GUI dependency)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from core.validators import validate_time_range  # noqa: E402


def test_valid_range():
    assert validate_time_range(0, 4)[0] is True


def test_start_equals_stop_invalid():
    assert validate_time_range(2, 2)[0] is False


def test_negative_start_invalid():
    assert validate_time_range(-1, 3)[0] is False


def test_stop_at_max_invalid():
    assert validate_time_range(0, 5)[0] is False


def test_start_greater_than_stop_invalid():
    assert validate_time_range(3, 1)[0] is False


def test_custom_max_stop():
    assert validate_time_range(0, 9, max_stop_exclusive=10)[0] is True
    assert validate_time_range(0, 10, max_stop_exclusive=10)[0] is False
