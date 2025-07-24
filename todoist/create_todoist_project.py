from .connection import api


def create_project(project_name):
    """Creates a Todoist project with the given name. Returns the Project object."""
    return api.add_project(name=project_name)


def get_project_by_name(project_name):
    """Find an existing Todoist project by name (case-insensitive). Returns the Project object or None."""
    projects = api.get_projects()
    for project in projects:
        if project.name.lower() == project_name.lower():
            return project
    return None
