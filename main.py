import os
from dotenv import load_dotenv
from gitlab.create_gitlab_notifications_db import init_db
from gitlab.fetch_gitlab_notifications_db import poll_once_and_save_events
from todoist.fetch_todoist_notification_db import poll_and_create_todoist_tasks

# import any other helper you want to test
load_dotenv()
db_file = os.getenv("GITLAB_NOTIFICATIONS_DB_FILE")


def main():
    init_db(db_file)

    # Try out any module, e.g.:
    poll_once_and_save_events(db_file, seen_ids=None)
    poll_and_create_todoist_tasks()


if __name__ == "__main__":
    main()
