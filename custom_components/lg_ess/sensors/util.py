from datetime import date, datetime


def _calculate_directional(direction: str, value: str) -> float:
    """Calculate the directional value based on the direction."""
    factor = 1
    if direction == "1":
        factor = -1
    return int(value) * factor


def _parse_date(raw_input: str) -> date:
    return datetime.strptime(raw_input, "%Y-%m-%d").date()

def _get(d, keys: list[str]):
  val = d
  for k in keys:
    if type(val) is dict:
      val = val.get(k)
    elif type(val) is list and k is int and 0 <= k < len(val):
      val = val[k]
    else:
      return val
  return val

def _or(option1, option2=None):
  val = option1()
  if (val is None) and (option2 is not None):
    val = option2()
  return val

def _mul(op1, op2):
    if (op1 is None) or (op2 is None):
        return None
    return op1 * op2