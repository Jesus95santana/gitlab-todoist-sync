import os
import requests
import time
from dotenv import load_dotenv

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


def get_project_events(project_id):
    url = f"{GITLAB_URL}/api/v4/projects/{project_id}/events"
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return resp.json()


def main():
    projects = get_my_projects()
    print(f"Found {len(projects)} projects.")
    seen_ids = {}  # project_id: set of event IDs

    for project in projects:
        seen_ids[project["id"]] = set()

    while True:
        try:
            for project in projects:
                events = get_project_events(project["id"])
                for event in events:
                    sid = seen_ids[project["id"]]
                    if event["id"] not in sid:
                        user = event["author"]["username"]
                        action = event["action_name"]
                        if action in ["pushed to", "deleted"]:
                            # Use branch/tag name from push_data.ref if present
                            push_data = event.get("push_data") or {}
                            target = push_data.get("ref") or ""
                        else:
                            target = event.get("target_title") or event.get("target_type") or ""
                        print(f"[{project['path_with_namespace']}] [{event['created_at']}] {user}: {action} {target}")
                        sid.add(event["id"])
            print("Waiting for next poll...")
        except Exception as e:
            print(f"Error: {e}")
        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
