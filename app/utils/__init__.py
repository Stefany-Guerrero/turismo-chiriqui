from datetime import datetime, timezone, timedelta

PANAMA_TZ = timezone(timedelta(hours=-5))

def panama_now():
    return datetime.now(PANAMA_TZ).replace(tzinfo=None)
