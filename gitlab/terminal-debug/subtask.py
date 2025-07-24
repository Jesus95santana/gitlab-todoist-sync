import os
from todoist_api_python.api import TodoistAPI
from dotenv import load_dotenv

load_dotenv()
api = TodoistAPI(os.getenv("TODOIST_TOKEN"))

PARENT_CONTENT = "Test Parent Task"

tasks = api.get_tasks()
parent_task = next((t for t in tasks if t.content == PARENT_CONTENT), None)

if parent_task:
    subtask = api.add_task(
        content="Subtask Example",
        project_id=parent_task.project_id,
        parent_id=parent_task.id,
    )
    print(f"Subtask created! {subtask.id}")
else:
    print("Parent task not found.")
