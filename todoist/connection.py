import os
from dotenv import load_dotenv


def get_todoist_headers():
    load_dotenv()
    token = os.getenv("TODOIST_TOKEN")
    if not token:
        raise Exception("Missing TODOIST_TOKEN in environment variables.")
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
