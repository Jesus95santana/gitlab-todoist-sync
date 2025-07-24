import os
from dotenv import load_dotenv
from todoist_api_python.api import TodoistAPI

load_dotenv()
_token = os.getenv("TODOIST_TOKEN")
if not _token:
    raise Exception("Missing TODOIST_TOKEN in environment variables.")

api = TodoistAPI(_token)
