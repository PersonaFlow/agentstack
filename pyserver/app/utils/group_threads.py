from typing import List, Optional
from pyserver.app.schema import Thread, GroupedThreads
from datetime import datetime, timedelta, timezone


def group_threads(
    threads: List[Thread], client_tz_offset: Optional[int] = 0
) -> GroupedThreads:
    grouped = {
        "Today": [],
        "Yesterday": [],
        "Past 7 Days": [],
        "Past 30 Days": [],
        "This Year": [],
        "Previous Years": [],
    }
    offset_hours = client_tz_offset / 60
    now = datetime.now(timezone.utc) - timedelta(hours=offset_hours)

    for thread in threads:
        updated_at = thread.updated_at
        if updated_at.tzinfo is None or updated_at.tzinfo.utcoffset(updated_at) is None:
            updated_at = updated_at.replace(tzinfo=timezone.utc)

        # Convert updated_at to UTC if it's not already
        if updated_at.tzinfo is None or updated_at.tzinfo.utcoffset(updated_at) is None:
            updated_at = updated_at.replace(tzinfo=timezone.utc)

        if updated_at.date() == now.date():
            grouped["Today"].append(thread)
        elif updated_at.date() == (now - timedelta(days=1)).date():
            grouped["Yesterday"].append(thread)
        elif now - timedelta(days=7) <= updated_at < now - timedelta(days=1):
            grouped["Past 7 Days"].append(thread)
        elif now - timedelta(days=30) <= updated_at < now - timedelta(days=7):
            grouped["Past 30 Days"].append(thread)
        elif updated_at.year == now.year:
            grouped["This Year"].append(thread)
        else:
            grouped["Previous Years"].append(thread)

    # Sorting each category by most recent first
    for category in grouped:
        grouped[category] = sorted(
            grouped[category], key=lambda x: x.updated_at, reverse=True
        )

    return grouped
