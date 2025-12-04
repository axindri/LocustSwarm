import random
from datetime import datetime, timedelta


def _random_supplier_id():
    suppliers = [
        10210,
        11035,
        114513,
        1145164,
        1181319,
        1181322,
        1298825,
        1304732,
        17887,
        36145,
        370729,
        42863,
        45256,
        807494,
    ]
    return random.choice(suppliers)


def _random_supplier_ids(cnt=2):
    return [_random_supplier_id() for _ in range(cnt)]


def _cur_week_monday_dt():
    today = datetime.now()
    return today - timedelta(days=today.weekday())


def _cur_week_monday_diff(weeks: int = 13):
    dt = _cur_week_monday_dt() - timedelta(weeks=weeks)
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def _random_date_from_week_monday(days_back=90):
    dt = (_cur_week_monday_dt().replace(hour=0, minute=0, second=0) - timedelta(days=1)) - timedelta(
        days=random.randint(0, days_back)
    )
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def _yesterday():
    dt = datetime.now().replace(hour=0, minute=0, second=0) - timedelta(days=1)
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def _cur_week_monday():
    dt = _cur_week_monday_dt().replace(hour=0, minute=0, second=0)
    return dt.strftime("%Y-%m-%d %H:%M:%S")
