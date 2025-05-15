from datetime import date, datetime


def _calculate_directional(direction: str, value: str) -> float:
    """Calculate the directional value based on the direction."""
    factor = 1
    if direction == "1":
        factor = -1
    return int(value) * factor


def _parse_date(raw_input: str) -> date:
    return datetime.strptime(raw_input, "%Y-%m-%d").date()
