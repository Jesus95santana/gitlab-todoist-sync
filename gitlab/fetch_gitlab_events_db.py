import requests
import sqlite3
import json
from gitlab.connection import get_gitlab_headers, get_gitlab_url


def save_event(note, project, kind, parent_title, branch, db_file):
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    # Use the exact GitLab API logic
    is_thread = int(note.get("type") == "DiscussionNote")
    c.execute(
        """
        INSERT OR IGNORE INTO events
        (id, project, kind, parent_title, author, body, branch, is_thread, created_at, json_blob)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            note["id"],
            project["path_with_namespace"],
            kind,
            parent_title,
            note["author"]["username"],
            note["body"],
            branch,
            is_thread,
            note["created_at"],
            json.dumps(note),
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


def get_open_merge_requests(project_id):
    headers = get_gitlab_headers()
    gitlab_url = get_gitlab_url()
    url = f"{gitlab_url}/api/v4/projects/{project_id}/merge_requests?state=opened&per_page=100"
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return resp.json()


def get_open_issues(project_id):
    headers = get_gitlab_headers()
    gitlab_url = get_gitlab_url()
    url = f"{gitlab_url}/api/v4/projects/{project_id}/issues?state=opened&per_page=100"
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return resp.json()


def get_mr_notes(project_id, mr_iid):
    headers = get_gitlab_headers()
    gitlab_url = get_gitlab_url()
    url = f"{gitlab_url}/api/v4/projects/{project_id}/merge_requests/{mr_iid}/notes"
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return resp.json()


def get_issue_notes(project_id, issue_iid):
    headers = get_gitlab_headers()
    gitlab_url = get_gitlab_url()
    url = f"{gitlab_url}/api/v4/projects/{project_id}/issues/{issue_iid}/notes"
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return resp.json()


def poll_once_and_save_events(db_file, seen_ids=None):
    """
    Polls GitLab for MR/issue comments (events), saves new user notes to db_file,
    and returns a list of new notes (for notification, etc).
    Only user comments or user-created threads are saved. System notes are skipped.
    """
    projects = get_my_projects()
    new_events = []

    if seen_ids is None:
        seen_ids = {}

    for project in projects:
        # MRs
        for mr in get_open_merge_requests(project["id"]):
            notes = get_mr_notes(project["id"], mr["iid"])
            key = (project["id"], "mr")
            if key not in seen_ids:
                seen_ids[key] = set()
            for note in notes:
                # Only allow user notes (not system notes)
                if note["id"] not in seen_ids[key] and not note.get("system", False):
                    save_event(note, project, "mr", mr["title"], mr.get("source_branch"), db_file)
                    new_events.append((note, project, "mr", mr["title"]))
                    seen_ids[key].add(note["id"])
        # Issues
        for issue in get_open_issues(project["id"]):
            notes = get_issue_notes(project["id"], issue["iid"])
            key = (project["id"], "issue")
            if key not in seen_ids:
                seen_ids[key] = set()
            for note in notes:
                # Only allow user notes (not system notes)
                if note["id"] not in seen_ids[key] and not note.get("system", False):
                    save_event(note, project, "issue", issue["title"], None, db_file)
                    new_events.append((note, project, "issue", issue["title"]))
                    seen_ids[key].add(note["id"])
    return new_events
