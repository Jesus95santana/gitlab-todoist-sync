import os
import sqlite3
from dotenv import load_dotenv

load_dotenv()

DB_FILE = os.getenv("GITLAB_EVENTS_DB_FILE")


def show_events(limit=100):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(
        """
        SELECT id, project, kind, parent_title, author, is_thread, created_at, body
        FROM events
        ORDER BY created_at DESC
        LIMIT ?
        """,
        (limit,),
    )
    rows = c.fetchall()
    for row in rows:
        # row: (id, project, kind, parent_title, author, is_thread, created_at, body)
        kind_label = "MR" if row[2] == "mr" else "ISSUE"
        thread_label = "THREAD" if row[5] else "COMMENT"
        print(f"[{kind_label}][{row[1]}] [{row[3]}] [{row[6]}] {row[4]}: {thread_label} - {row[7]}")
    conn.close()


if __name__ == "__main__":
    show_events()
