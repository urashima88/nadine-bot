import re
from datetime import datetime, timedelta

from psycopg2.extras import NumericRange

UNIT_EXCEPTIONS_OTHER = {"11", "12", "13", "14"}
UNIT_EXCEPTIONS_234 = {"2", "3", "4"}

def get_production_time_days_ru_format(
    production_time: NumericRange, 
    unit_1: str, # for 1 production_time unit
    unit_234: str, # for 2 | 3 | 4 production_time units
    unit_other: str # for other production_time units
):
    upper_last_digits = str(int(production_time.upper))[-2:]
    if upper_last_digits in UNIT_EXCEPTIONS_OTHER:
        return unit_other
    elif upper_last_digits[-1] in UNIT_EXCEPTIONS_234:
        return unit_234
    elif upper_last_digits[-1] == 1:
        return unit_1
    return unit_other

def str_to_numeric_range(range_str: str) -> NumericRange | None:
    if not range_str or range_str == 'empty':
        return None
    match = re.match(r'([\[\(])(\d+),(\d+)([\])])', range_str)
    if not match:
        return None
    left_bound, lower_str, upper_str, right_bound = match.groups()
    lower = int(lower_str)
    upper = int(upper_str)
    lower_inc = (left_bound == '[')
    upper_inc = (right_bound == ']')
    bounds = f"{'[' if lower_inc else '('}{']' if upper_inc else ')'}"
    return NumericRange(lower, upper, bounds=bounds)

def format_local_datetime(dt: datetime, timezone_str: str) -> str:
    match = re.match(r'UTC([+-])(\d+)', timezone_str)
    if not match:
        return dt.strftime("%d.%m.%Y в %H:%M (UTC)")
    sign, hours = match.groups()
    offset_hours = int(hours) * (1 if sign == '+' else -1)
    local_dt = dt + timedelta(hours=offset_hours)
    return local_dt.strftime(f"%d.%m.%Y в %H:%M (UTC{sign}{hours})")