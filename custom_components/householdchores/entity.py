from datetime import datetime, timedelta, timezone
from .const import STATUSES

def parse_datetime(dt_str):
    """Parse an ISO datetime string safely."""
    if not dt_str:
        return None
    try:
        # Try to support timezone-aware parsing
        return datetime.fromisoformat(dt_str)
    except Exception:
        return None

def calculate_status(next_due):
    """Calculate the status of a chore based on its next due date."""
    if not next_due:
        return STATUSES["DO_NOT_DO"]

    now = datetime.now(timezone.utc)
    delta = next_due - now

    if delta.total_seconds() < -172800:  # More than 48h past
        return STATUSES["OVERDUE"]
    elif delta.total_seconds() < 0:
        return STATUSES["DUE"]
    elif delta.total_seconds() < 86400:  # Within 24h
        return STATUSES["DUE_SOON"]
    else:
        return STATUSES["NOT_DUE"]
