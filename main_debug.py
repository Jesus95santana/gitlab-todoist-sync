import time
import os
from dotenv import load_dotenv
from gitlab.create_gitlab_notifications_db import init_db
from gitlab.fetch_gitlab_notifications_db import poll_once_and_save_events
from todoist.fetch_todoist_notification_db import poll_and_create_todoist_tasks

# import any other helper you want to test
load_dotenv()
db_file = os.getenv("GITLAB_NOTIFICATIONS_DB_FILE")


def main():
    while True:
        init_db(db_file)

        # Try out any module, e.g.:
        poll_once_and_save_events(db_file, seen_ids=None)

        # Parameter here is how far back in hours to get notifications
        poll_and_create_todoist_tasks(2)
        time.sleep(60)


if __name__ == "__main__":
    main()
