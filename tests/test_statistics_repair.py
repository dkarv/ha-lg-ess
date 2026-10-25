from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import pytest

from custom_components.lg_ess.statistics_repair import dst_shift_in_month, find_double_counted

BERLIN = ZoneInfo("Europe/Berlin")


@pytest.mark.parametrize("month_start, expected", [
    (datetime(2026, 10, 1, tzinfo=BERLIN), datetime(2026, 10, 25, 1, tzinfo=timezone.utc)),
    (datetime(2026, 3, 1, tzinfo=BERLIN), datetime(2026, 3, 29, 1, tzinfo=timezone.utc)),
    (datetime(2026, 7, 1, tzinfo=BERLIN), None),
    (datetime(2026, 10, 1, tzinfo=timezone.utc), None),
])
def test_dst_shift_in_month(month_start, expected):
    assert dst_shift_in_month(month_start) == expected


def _rows(*state_sum):
    return [{"start": float(i * 3600), "state": state, "sum": sum} for i, (state, sum) in enumerate(state_sum)]


def test_jump_after_reset():
    rows = _rows(
        (880, 5000),  # before the shift
        (2, 5002),  # device reset the counter: new cycle
        (5, 5005),
        (906, 5906),  # graph restores the month total: the 880 before the shift are counted again
        (910, 5910),
    )
    assert find_double_counted(rows) == (3 * 3600, -880)


def test_already_repaired():
    rows = _rows((880, 5000), (2, 5002), (5, 5005), (906, 5006), (910, 5010))
    assert find_double_counted(rows) is None


def test_month_total_not_restored_yet():
    # Still on the old version, the sensor shows the reset counter
    rows = _rows((880, 5000), (2, 5002), (5, 5005), (30, 5030))
    assert find_double_counted(rows) is None


def test_no_reset():
    rows = _rows((880, 5000), (885, 5005), (890, 5010))
    assert find_double_counted(rows) is None


def test_missing_values():
    rows = _rows((880, 5000), (None, None), (906, 5906))
    assert find_double_counted(rows) is None
    assert find_double_counted(rows[:1]) is None
