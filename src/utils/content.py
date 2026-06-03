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