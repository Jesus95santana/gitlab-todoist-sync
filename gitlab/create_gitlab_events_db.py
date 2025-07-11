import sqlite3


def init_db(db_file):
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY,
            project TEXT,
            kind TEXT,        -- "mr" or "issue"
            parent_title TEXT,
            author TEXT,
            body TEXT,
            is_thread INTEGER,
            created_at TEXT,
            json_blob TEXT,
            processed INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()
    print(f"Database '{db_file}' initialized.")
