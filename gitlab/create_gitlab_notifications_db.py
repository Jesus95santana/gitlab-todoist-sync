import sqlite3


def init_db(db_file):
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY,
            project TEXT,
            user TEXT,
            action TEXT,
            target TEXT,
            time TEXT,
            json_blob TEXT
        )
    """)
    conn.commit()
    conn.close()
    print(f"Database '{db_file}' initialized.")
