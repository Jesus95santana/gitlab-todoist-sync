from .connection import api


def create_task(
    content,
    project_id,
    labels=None,
    priority=None,
    due_date=None,
    description=None,
    assignee_id=None,
    parent_id=None,
):
    """
    Creates a Todoist task (or subtask if parent_id is given) using the Todoist Python SDK.
    Returns the Task object.
    """
    return api.add_task(
        content=content,
        project_id=project_id,
        labels=labels,
        priority=priority,
        due_date=due_date,
        description=description,
        assignee_id=assignee_id,
        parent_id=parent_id,
    )
