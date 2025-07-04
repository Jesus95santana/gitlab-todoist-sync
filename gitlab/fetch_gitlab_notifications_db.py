import requests
import sqlite3
import json
from gitlab.connection import get_gitlab_headers, get_gitlab_url


def save_event(event, project, db_file):
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    c.execute(
        """
        INSERT OR IGNORE INTO events (id, project, user, action, target, time, json_blob)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            event["id"],
            project["path_with_namespace"],
            event["author"]["username"],
            event["action_name"],
            event.get("target_title") or event.get("target_type"),
            event["created_at"],
            json.dumps(event),
        ),
    )
    conn.commit()
    conn.close()


def get_my_projects():
    headers = get_gitlab_headers()
    gitlab_url = get_gitlab_url()
    projects = []
    page = 1
    while True:
        url = f"{gitlab_url}/api/v4/projects?membership=true&simple=true&per_page=100&page={page}"
        resp = requests.get(url, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        if not data:
            break
        projects.extend(data)
        page += 1
    return projects


def get_project_events(project_id):
    headers = get_gitlab_headers()
    gitlab_url = get_gitlab_url()
    url = f"{gitlab_url}/api/v4/projects/{project_id}/events"
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return resp.json()


def poll_once_and_save_events(db_file, seen_ids=None):
    """
    Polls GitLab projects *once*, saves new events to db_file,
    and returns a list of new events (for notification, etc).
    """
    projects = get_my_projects()
    new_events = []

    if seen_ids is None:
        seen_ids = {project["id"]: set() for project in projects}

    for project in projects:
        events = get_project_events(project["id"])
        for event in events:
            sid = seen_ids[project["id"]]
            if event["id"] not in sid:
                save_event(event, project, db_file)
                new_events.append((event, project))
                sid.add(event["id"])

    return new_events
