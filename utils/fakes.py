import random

from datetime import datetime, timedelta


def get_port_from_range(start=8080, end=8090):
    return random.randint(start, end)


def _random_supplier_id():
    return random.randint(10000, 11000)


def _constant_supplier_id():
    return 10465


def _constant_supplier_ids():
    return [10465, 10612]


def _random_supplier_ids(cnt=2):
    return [_random_supplier_id() for _ in range(cnt)]


def _cur_week_monday_dt():
    today = datetime.now()
    return today - timedelta(days=today.weekday())


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
