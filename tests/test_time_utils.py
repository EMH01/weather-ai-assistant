from datetime import UTC, datetime

from weather_assistant.time_utils import current_time_in_zone, local_time_from_offset


def test_named_timezone_conversion():
    reference = datetime(2026, 1, 15, 12, 0, tzinfo=UTC)
    local = current_time_in_zone("Europe/Madrid", now=reference)
    assert local.hour == 13
    assert local.utcoffset().total_seconds() == 3600


def test_numeric_offset_conversion():
    reference = datetime(2026, 1, 15, 12, 0, tzinfo=UTC)
    local = local_time_from_offset(7200, now=reference)
    assert local.hour == 14
