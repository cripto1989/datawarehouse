import pytest
from dates import get_date_range, validate_datetime_string


def test_get_date_range():
    today = "2026-05-10"
    start_time, end_time = get_date_range(today)

    assert start_time == "2026-05-09T23:00:00"
    assert end_time == "2026-05-10T22:59:59"


def test_validate_datetime_string():
    valid_datetime = "2026-05-10T15:30:00"
    value = validate_datetime_string(valid_datetime)
    assert value == valid_datetime


def test_validate_datetime_string_with_wrong_value():
    valid_datetime = "2026-05-1"

    with pytest.raises(ValueError) as exc_info:
        validate_datetime_string(valid_datetime)
    assert str(exc_info.value) == "datetime must be a valid datetime string in the format YYYY-MM-DDTHH:MM:SS."
