from datetime import datetime, timedelta, timezone
from .const import STATUSES

def parse_datetime(dt_str):
    if not dt_str:
        return None
    try:
        return datetime.fromisoformat(dt_str)
    except Exception:
        return None

def calculate_status(next_due):
    if not next_due:
        return STATUSES["DO_NOT_DO"]

    now = datetime.now(timezone.utc)
    delta = next_due - now

    if delta.total_seconds() < -172800:  # > 48h past
        return STATUSES["OVERDUE"]
    elif delta.total_seconds() < 0:
        return STATUSES["DUE"]
    elif delta.total_seconds() < 86400:  # within 24h
        return STATUSES["DUE_SOON"]
    else:
        return STATUSES["NOT_DUE"]
