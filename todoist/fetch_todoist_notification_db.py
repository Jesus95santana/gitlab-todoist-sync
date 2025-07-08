import os
import sqlite3
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from .create_todoist_task import create_task
from .create_todoist_project import get_project_by_name, create_project
from linux.notify_gitlab_event import notify_gitlab_event

load_dotenv()


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
    c.execute("SELECT id, project, user, action, target, time FROM events WHERE time >= ? ORDER BY time ASC", (one_hour_ago,))
    rows = c.fetchall()
    conn.close()

    print(f"Found {len(rows)} notification(s) in the last hour(s).")

    for row in rows:
        event_id, project_name, user, action, target, event_time = row
        content = f"{project_name}: {user} {action} {target} [{event_time}]"
        # Optional: set priority, labels, etc
        task = create_task(
            content=content,
            project_id=project_id,
            priority=3,  # Example default
            # labels=[...], etc.
        )
        notify_gitlab_event()
        print(f"Created Todoist task for event {event_id}")
