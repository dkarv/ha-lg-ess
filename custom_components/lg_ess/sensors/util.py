from datetime import date, datetime

import logging
_LOGGER = logging.getLogger(__name__)

def _calculate_directional(direction: str, value: str) -> float:
    """Calculate the directional value based on the direction."""
    factor = 1
    if direction == "1":
        factor = -1
    return int(value) * factor


def _parse_date(raw_input: str) -> date:
    print(f"Parsing date from input: {raw_input}")
    return datetime.strptime(raw_input, "%Y-%m-%d").date()


def _get(d, keys: list):
    val = d
    for k in keys:
        if type(val) is dict:
            val = val.get(k)
        elif type(val) is list and type(k) is int and 0 <= k < len(val):
            val = val[k]
        else:
            return None
    return val


def _or(option1, option2=None):
    val = option1()
    if (val is None) and (option2 is not None):
        val = option2()
    return val


def _mul(op1, op2):
    if (op1 is None) or (op2 is None):
        return None
    return int(op1) * int(op2)


def _get_bool(d, keys: list):
    val = _get(d, keys)
    if val == "on" or val == "1":
        return True
    if val == "off" or val == "0":
        return False
    if val is not None:
        _LOGGER.warning(f"Unexpected boolean value: {val} for keys: {keys}")
    return None

def _get_int(d, keys: list):
    val = _get(d, keys)
    if val is not None:
        return int(val)
    return None
