def in_quiet_hours(hour: int, start_hour: int, end_hour: int) -> bool:
    if not 0 <= hour <= 23:
        raise ValueError("hour must be in [0, 23]")

    if start_hour == end_hour:
        return False

    # BUG: this only works for windows that do not cross midnight.
    return start_hour <= hour < end_hour
