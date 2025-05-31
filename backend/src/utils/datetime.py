from datetime import datetime
from pytz import timezone
from cores.config import env

def get_current_datetime() -> datetime:
    return datetime.now(timezone(env.TIMEZONE))

def convert_datetime_to_str(dt: datetime, tz: str = env.TIMEZONE) -> str:
    return dt.astimezone(timezone(tz)).strftime("%Y-%m-%d %H:%M:%S")

def convert_str_to_datetime(dt_str: str) -> datetime:
    tz = timezone(env.TIMEZONE)
    naive_dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
    return tz.localize(naive_dt)
