import requests
from .connection import get_todoist_headers


def create_task(
    content,
    project_id,
    labels=None,
    priority=None,
    due_date=None,
    description=None,
    assignee_id=None,
):
    url = "https://api.todoist.com/rest/v2/tasks"
    headers = get_todoist_headers()
    data = {
        "content": content,
        "project_id": project_id,
    }
    if labels:
        data["labels"] = labels
    if priority:
        data["priority"] = priority
    if due_date:
        data["due_date"] = due_date
    if description:
        data["description"] = description
    if assignee_id:
        data["assignee_id"] = assignee_id

    resp = requests.post(url, headers=headers, json=data)
    resp.raise_for_status()
    return resp.json()
