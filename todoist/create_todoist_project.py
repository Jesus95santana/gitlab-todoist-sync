import requests
from .connection import get_todoist_headers


def create_project(project_name):
    url = "https://api.todoist.com/rest/v2/projects"
    headers = get_todoist_headers()
    data = {"name": project_name}
    resp = requests.post(url, headers=headers, json=data)
    resp.raise_for_status()
    return resp.json()


def get_project_by_name(project_name):
    url = "https://api.todoist.com/rest/v2/projects"
    headers = get_todoist_headers()
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    for project in resp.json():
        if project["name"].lower() == project_name.lower():
            return project
    return None
