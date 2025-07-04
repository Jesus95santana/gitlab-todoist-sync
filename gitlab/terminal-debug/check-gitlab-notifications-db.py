import os
import sqlite3
from dotenv import load_dotenv

load_dotenv()

DB_FILE = os.getenv("GITLAB_NOTIFICATIONS_DB_FILE")


def show_events(limit=100):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(
        """
        SELECT id, project, user, action, target, time
        FROM events
        ORDER BY time DESC
        LIMIT ?
    """,
        (limit,),
    )
    rows = c.fetchall()
    for row in rows:
        print(f"[{row[1]}] [{row[5]}] {row[2]}: {row[3]} {row[4]}")
    conn.close()


if __name__ == "__main__":
    show_events()
