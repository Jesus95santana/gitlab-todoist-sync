import os
import sqlite3
import re
import json
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from dotenv import load_dotenv
from .create_todoist_task import create_task
from .create_todoist_project import get_project_by_name, create_project
from .create_todoist_label import get_label_by_name, create_label
from linux.notify_gitlab_event import notify_gitlab_event

load_dotenv()


def prettify_timestamp(timestr):
    try:
        dt = datetime.fromisoformat(timestr.replace("Z", "+00:00"))
        dt = dt.astimezone(ZoneInfo("America/New_York"))
        return dt.strftime("%-m/%-d/%y %-I:%M%p %Z")
    except Exception:
        return timestr


def extract_branch_name(parent_title, body=None):
    """
    Attempts to extract a branch name from the parent_title.
    """
    match = re.search(r"Draft:\s*([^\s/]+\/[^\s]+)", parent_title)
    if match:
        return match.group(1)
    # Fallback: last word after slash
    parts = parent_title.split("/")
    if len(parts) > 1:
        return parts[-1].strip()
    return None


def poll_and_create_todoist_event_tasks(TimeHours):
    db_file = os.getenv("GITLAB_EVENTS_DB_FILE")
    project_name = os.getenv("TODOIST_EVENT_PROJECT_NAME")

    # Get (or create) the Todoist project
    project = get_project_by_name(project_name)
    if not project:
        project = create_project(project_name)
    project_id = project["id"]

    # Connect to DB and select unprocessed USER events from the last N hours
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    time_limit = (datetime.now(timezone.utc) - timedelta(hours=TimeHours)).isoformat()
    c.execute(
        """
        SELECT id, project, kind, parent_title, author, is_thread, created_at, body, json_blob
        FROM events
        WHERE created_at >= ? AND processed=0
        ORDER BY created_at ASC
        """,
        (time_limit,),
    )
    rows = c.fetchall()

    print(f"Found {len(rows)} unprocessed event(s) in the last {TimeHours} hour(s).")

    for row in rows:
        event_id, project_name, kind, parent_title, author, is_thread, created_at, body, json_blob = row

        # Load the raw note JSON for user/system check
        note_data = {}
        try:
            note_data = json.loads(json_blob)
        except Exception:
            pass

        # ---- Only handle USER notes (not system) ----
        if note_data.get("system", False):
            continue

        pretty_time = prettify_timestamp(created_at)
        # FIXED: explicit bool cast for labeling
        thread_label = "THREAD" if bool(is_thread) else "COMMENT"
        kind_label = "MR" if kind == "mr" else "ISSUE"

        # Task title: concise, just meta and branch/project
        content = f"[{kind_label}][{thread_label}] {project_name}"

        # Task description: everything else, keep markdown/code formatting
        description = f"[{pretty_time}]\n{parent_title}\n{body}"

        # --- Branch label logic ---
        branch_only = extract_branch_name(parent_title, body)
        branch_name = f"{project_name}:{branch_only}" if branch_only else None

        label_names = []
        if branch_name and branch_name.strip() and not branch_name.strip().isdigit():
            label = get_label_by_name(branch_name)
            if not label:
                label = create_label(branch_name)
            if label:
                label_names = [branch_name]

        task = create_task(content=content, project_id=project_id, priority=4 if bool(is_thread) else 3, description=description, labels=label_names)
        notify_gitlab_event("New Event")
        print(f"Created Todoist task for event {event_id} (label: {branch_name if branch_name else 'none'})")

        # Mark as processed
        c.execute("UPDATE events SET processed=1 WHERE id=?", (event_id,))
        conn.commit()

    conn.close()
