import os
import sqlite3
import re
import json
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from dotenv import load_dotenv
from .create_todoist_project import get_project_by_name, create_project
from .create_todoist_label import get_label_by_name, create_label
from .connection import api  # SDK client object from connection.py
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
    match = re.search(r"Draft:\s*([^\s/]+\/[^\s]+)", parent_title)
    if match:
        return match.group(1)
    parts = parent_title.split("/")
    if len(parts) > 1:
        return parts[-1].strip()
    return None


def poll_and_create_todoist_event_tasks(TimeHours):
    db_file = os.getenv("GITLAB_EVENTS_DB_FILE")
    project_name = os.getenv("TODOIST_EVENT_PROJECT_NAME")

    project = get_project_by_name(project_name)
    if not project:
        project = create_project(project_name)
    # Use attribute access for SDK Project object
    project_id = project.id

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

        note_data = {}
        try:
            note_data = json.loads(json_blob)
        except Exception:
            pass

        if note_data.get("system", False):
            continue

        pretty_time = prettify_timestamp(created_at)
        thread_label = "THREAD" if bool(is_thread) else "COMMENT"
        kind_label = "MR" if kind == "mr" else "ISSUE"
        content = f"[{kind_label}][{thread_label}] {project_name}"
        description = f"[{pretty_time}]\n{parent_title}\n{body}"

        branch_only = extract_branch_name(parent_title, body)
        branch_name = f"{project_name}:{branch_only}" if branch_only else None

        label_names = []
        if branch_name and branch_name.strip() and not branch_name.strip().isdigit():
            label = get_label_by_name(branch_name)
            if not label:
                label = create_label(branch_name)
            if label:
                label_names = [branch_name]

        # --- MAIN TASK ---
        task = api.add_task(
            content=content,
            project_id=project_id,
            priority=4 if bool(is_thread) else 3,
            description=description,
            labels=label_names,
        )
        notify_gitlab_event("New Event")
        print(f"Created Todoist task for event {event_id} (label: {branch_name if branch_name else 'none'})")

        # --- SUBTASKS: Checklist items in the body ---
        checklist_pattern = r"^\s*[*\-]\s*\[( |x)\]\s*(.+)$"
        lines = body.splitlines()
        for line in lines:
            m = re.match(checklist_pattern, line, re.IGNORECASE)
            if m:
                subtask_content = m.group(2).strip()
                checked = m.group(1).lower() == "x"
                subtask = api.add_task(
                    content=subtask_content,
                    project_id=project_id,
                    parent_id=task.id,  # Use the SDK's task.id
                    priority=3,
                    description="",
                    labels=label_names,
                )
                if checked:
                    api.close_task(subtask.id)  # Mark subtask as complete

        # Mark as processed
        c.execute("UPDATE events SET processed=1 WHERE id=?", (event_id,))
        conn.commit()

    conn.close()
