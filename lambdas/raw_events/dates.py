from datetime import datetime, timedelta


def get_date_range(date: str) -> tuple[str, str]:
    """
    Convert a date string (YYYY-MM-DD) into a start/end datetime range.

    The start datetime is the previous day at 23:00:00.
    The end datetime is the provided day at 22:59:59.

    Returns:
        Tuple of (start_datetime, end_datetime) formatted as:
        %Y-%m-%dT%H:%M:%S
    """

    date_obj = datetime.strptime(date, "%Y-%m-%d")

    start_datetime = (date_obj - timedelta(days=1)).replace(hour=23, minute=0, second=0, microsecond=0)
    end_datetime = date_obj.replace(hour=22, minute=59, second=59, microsecond=0)

    start_str = start_datetime.strftime("%Y-%m-%dT%H:%M:%S")
    end_str = end_datetime.strftime("%Y-%m-%dT%H:%M:%S")

    return start_str, end_str


def validate_datetime_string(value: str, field_name: str = "datetime") -> str:
    """
    Validate a datetime string in the exact format YYYY-MM-DDTHH:MM:SS.

    Parameters
    ----------
    value : str
        The datetime string to validate.
    field_name : str
        The name of the field being validated, used in error messages.

    Returns
    -------
    str
        The validated datetime string.

    Raises
    ------
    ValueError
        If the value is not a string or does not match the expected format.
    """
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a string in the format YYYY-MM-DDTHH:MM:SS.")

    try:
        parsed_value = datetime.strptime(value, "%Y-%m-%dT%H:%M:%S")
    except ValueError as exc:
        raise ValueError(f"{field_name} must be a valid datetime string in the format YYYY-MM-DDTHH:MM:SS.") from exc

    if parsed_value.strftime("%Y-%m-%dT%H:%M:%S") != value:
        raise ValueError(f"{field_name} must match the exact format YYYY-MM-DDTHH:MM:SS.")

    return value


def validate_time_range(start_time: str, end_time: str) -> None:
    """
    Validate that end_time is greater than start_time.

    Parameters
    ----------
    start_time : str
        Start datetime string in the format YYYY-MM-DDTHH:MM:SS.
    end_time : str
        End datetime string in the format YYYY-MM-DDTHH:MM:SS.

    Raises
    ------
    ValueError
        If end_time is not greater than start_time.
    """
    start_dt = datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%S")
    end_dt = datetime.strptime(end_time, "%Y-%m-%dT%H:%M:%S")

    if end_dt <= start_dt:
        raise ValueError("end_time must be greater than start_time.")
