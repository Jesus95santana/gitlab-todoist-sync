import os
import requests
import time
from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta

# === Load environment variables ===
load_dotenv()
GITLAB_URL = os.getenv("GITLAB_URL")
PAT_TOKEN = os.getenv("PRIVATE_TOKEN")
POLL_INTERVAL = 60  # seconds

headers = {"PRIVATE-TOKEN": PAT_TOKEN}


def get_my_projects():
    projects = []
    page = 1
    while True:
        url = f"{GITLAB_URL}/api/v4/projects?membership=true&simple=true&per_page=100&page={page}"
        resp = requests.get(url, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        if not data:
            break
        projects.extend(data)
        page += 1
    return projects


def get_open_merge_requests(project_id):
    url = f"{GITLAB_URL}/api/v4/projects/{project_id}/merge_requests?state=opened&per_page=100"
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return resp.json()


def get_open_issues(project_id):
    url = f"{GITLAB_URL}/api/v4/projects/{project_id}/issues?state=opened&per_page=100"
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return resp.json()


def get_mr_notes(project_id, mr_iid):
    url = f"{GITLAB_URL}/api/v4/projects/{project_id}/merge_requests/{mr_iid}/notes"
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return resp.json()


def get_issue_notes(project_id, issue_iid):
    url = f"{GITLAB_URL}/api/v4/projects/{project_id}/issues/{issue_iid}/notes"
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return resp.json()


def main():
    projects = get_my_projects()
    print(f"Found {len(projects)} projects.")
    seen_note_ids = {}  # (project_id, type, iid): set of note IDs

    for project in projects:
        seen_note_ids[(project["id"], "mr")] = set()
        seen_note_ids[(project["id"], "issue")] = set()

    while True:
        try:
            now = datetime.now(timezone.utc)
            for project in projects:
                # Merge Requests
                mrs = get_open_merge_requests(project["id"])
                for mr in mrs:
                    notes = get_mr_notes(project["id"], mr["iid"])
                    sid = seen_note_ids[(project["id"], "mr")]
                    for note in notes:
                        if note["id"] not in sid:
                            note_time = datetime.fromisoformat(note["created_at"].replace("Z", "+00:00"))
                            if (now - note_time) <= timedelta(hours=2):
                                is_thread = bool(note.get("discussion_id") and note.get("position"))
                                print(
                                    f"[MR][{project['path_with_namespace']}] [{mr['title']}] [{note['created_at']}] {note['author']['username']}: {'THREAD' if is_thread else 'COMMENT'} - {note['body']}"
                                )
                            sid.add(note["id"])
                # Issues
                issues = get_open_issues(project["id"])
                for issue in issues:
                    notes = get_issue_notes(project["id"], issue["iid"])
                    sid = seen_note_ids[(project["id"], "issue")]
                    for note in notes:
                        if note["id"] not in sid:
                            note_time = datetime.fromisoformat(note["created_at"].replace("Z", "+00:00"))
                            if (now - note_time) <= timedelta(hours=2):
                                is_thread = bool(note.get("discussion_id") and note.get("position"))
                                print(
                                    f"[ISSUE][{project['path_with_namespace']}] [{issue['title']}] [{note['created_at']}] {note['author']['username']}: {'THREAD' if is_thread else 'COMMENT'} - {note['body']}"
                                )
                            sid.add(note["id"])
            print("Waiting for next poll...")
        except Exception as e:
            print(f"Error: {e}")
        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
