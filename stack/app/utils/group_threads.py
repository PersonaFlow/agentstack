from typing import List, Optional
from stack.app.schema.thread import Thread, GroupedThreads
from datetime import datetime, timedelta, timezone

def group_threads(
    threads: List[Thread], client_tz_offset: int = 0
) -> GroupedThreads:
    
    grouped = {
        "Today": [],
        "Yesterday": [],
        "Past 7 Days": [],
        "Past 30 Days": [],
        "This Year": [],
        "Previous Years": [],
    }
    
    # Adjusting for the client's timezone offset
    client_tz = timezone(timedelta(minutes=client_tz_offset))
    now_utc = datetime.now(timezone.utc)
    now_in_user_tz = now_utc.astimezone(client_tz)
    
    def to_user_tz(dt: datetime) -> datetime:
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(client_tz)
    
    for thread in threads:
        updated_at_user_tz = to_user_tz(thread.updated_at)
        updated_at_date = updated_at_user_tz.date()
        
        if updated_at_date == now_in_user_tz.date():
            grouped["Today"].append(thread)
        elif updated_at_date == (now_in_user_tz - timedelta(days=1)).date():
        elif updated_at_date == (now_in_user_tz - timedelta(days=1)).date():
            grouped["Yesterday"].append(thread)
        elif (now_in_user_tz - timedelta(days=7)).date() <= updated_at_date < (now_in_user_tz - timedelta(days=1)).date():
        elif (now_in_user_tz - timedelta(days=7)).date() <= updated_at_date < (now_in_user_tz - timedelta(days=1)).date():
            grouped["Past 7 Days"].append(thread)
        elif (now_in_user_tz - timedelta(days=30)).date() <= updated_at_date < (now_in_user_tz - timedelta(days=7)).date():
        elif (now_in_user_tz - timedelta(days=30)).date() <= updated_at_date < (now_in_user_tz - timedelta(days=7)).date():
            grouped["Past 30 Days"].append(thread)
        elif updated_at_user_tz.year == now_in_user_tz.year:
        elif updated_at_user_tz.year == now_in_user_tz.year:
            grouped["This Year"].append(thread)
        else:
            grouped["Previous Years"].append(thread)
    
    # Sorting each category by most recent first
    for category in grouped:
        grouped[category] = sorted(
            grouped[category], key=lambda x: x.updated_at, reverse=True
        )
    
    return grouped

