import time
import os
from dotenv import load_dotenv

# Notification Alerts
from gitlab.create_gitlab_notifications_db import init_db as init_notification_db
from gitlab.fetch_gitlab_notifications_db import poll_once_and_save_events as poll_and_save_notifications
from todoist.fetch_todoist_notification_db import poll_and_create_todoist_tasks as poll_and_create_todoist_notification_tasks

# Event Alerts
from gitlab.create_gitlab_events_db import init_db as init_events_db
from gitlab.fetch_gitlab_events_db import poll_once_and_save_events as poll_and_save_events
from todoist.fetch_todoist_event_db import poll_and_create_todoist_event_tasks as poll_and_create_todoist_event_tasks


# import any other helper you want to test
load_dotenv()
db_notifications_file = os.getenv("GITLAB_NOTIFICATIONS_DB_FILE")
db_events_file = os.getenv("GITLAB_EVENTS_DB_FILE")


def main():
    while True:
        # Notifications
        init_notification_db(db_notifications_file)
        poll_and_save_notifications(db_notifications_file, seen_ids=None)
        # Parameter here is how far back in hours to get notifications
        poll_and_create_todoist_notification_tasks(2)

        # Events
        init_events_db(db_events_file)
        poll_and_save_events(db_events_file, seen_ids=None)
        poll_and_create_todoist_event_tasks(2)

        time.sleep(60)


if __name__ == "__main__":
    main()
