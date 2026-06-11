from datetime import datetime, timedelta

import pytz


def get_beijing_time():
    beijing_tz = pytz.timezone("Asia/Shanghai")
    current_bj_time = datetime.now(beijing_tz)
    return current_bj_time.strftime("%Y-%m-%d %H:%M")


def get_beijing_date_str():
    now = datetime.now(pytz.timezone("Asia/Shanghai"))
    return f"{now.year}-{now.month}-{now.day}"


def get_current_date():
    current_date = datetime.now()
    return current_date.strftime("%Y-%m-%d")


def get_current_and_future_dates(days=7):
    current_date = datetime.now()
    future_date = current_date + timedelta(days=days)
    return current_date.strftime("%Y-%m-%d"), future_date.strftime("%Y-%m-%d")


__all__ = [
    "get_beijing_date_str",
    "get_beijing_time",
    "get_current_and_future_dates",
    "get_current_date",
]
