import os
import sqlite3
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from dotenv import load_dotenv
from .create_todoist_task import create_task
from .create_todoist_project import get_project_by_name, create_project
from linux.notify_gitlab_event import notify_gitlab_event

load_dotenv()


def prettify_timestamp(timestr):
    try:
        # Parse UTC time
        dt = datetime.fromisoformat(timestr.replace("Z", "+00:00"))
        # Convert to New York time (handles EST/EDT)
        dt = dt.astimezone(ZoneInfo("America/New_York"))
        return dt.strftime("%-m/%-d/%y %-I:%M%p %Z")
    except Exception:
        return timestr


def poll_and_create_todoist_tasks(TimeHours):
    db_file = os.getenv("GITLAB_NOTIFICATIONS_DB_FILE")
    project_name = os.getenv("TODOIST_NOTIFICATION_PROJECT_NAME")

    # Get (or create) the Todoist project
    project = get_project_by_name(project_name)
    if not project:
        project = create_project(project_name)
    project_id = project["id"]

    # Connect to DB and select notifications from last hour
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    one_hour_ago = (datetime.now(timezone.utc) - timedelta(hours=TimeHours)).isoformat()
    c.execute("SELECT id, project, user, action, target, time FROM events WHERE time >= ? AND processed=0 ORDER BY time ASC", (one_hour_ago,))
    rows = c.fetchall()

    print(f"Found {len(rows)} unprocessed notification(s) in the last {TimeHours} hour(s).")

    for row in rows:
        event_id, project_name, user, action, target, event_time = row
        pretty_time = prettify_timestamp(event_time)
        content = f"{project_name}: {user} {action} {target} [{pretty_time}]"
        task = create_task(
            content=content,
            project_id=project_id,
            priority=3,
        )
        notify_gitlab_event("New Notification")
        print(f"Created Todoist task for event {event_id}")

        # Mark as processed
        c.execute("UPDATE events SET processed=1 WHERE id=?", (event_id,))
        conn.commit()

    conn.close()
