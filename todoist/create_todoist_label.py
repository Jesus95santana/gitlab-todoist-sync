import os
from todoist_api_python.api import TodoistAPI

api = TodoistAPI(os.getenv("TODOIST_TOKEN"))


def get_label_by_name(name):
    """Return the label object with this name, or None if not found."""
    labels = api.get_labels()
    for label in labels:
        if label.name.lower() == name.lower():
            return label
    return None


def create_label(name):
    """Create a new label by name (if it does not exist). Returns the new label object."""
    try:
        label = api.add_label(name)
        return label
    except Exception as e:
        print(f"Error creating label '{name}': {e}")
        return None
