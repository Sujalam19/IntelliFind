import sqlite3
import os

# Remove old database files and locks if they exist
def cleanup_db_locks():
    for file in ["lostfound.db-wal", "lostfound.db-shm"]:
        if os.path.exists(file):
            try:
                os.remove(file)
            except:
                pass

cleanup_db_locks()

def get_db():
    conn = sqlite3.connect("lostfound.db", timeout=20.0, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    # Enable WAL mode for better concurrency
    conn.execute("PRAGMA journal_mode=WAL")
    # Set synchronous mode to NORMAL (faster but still safe)
    conn.execute("PRAGMA synchronous=NORMAL")
    # Increase cache size
    conn.execute("PRAGMA cache_size=5000")
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT UNIQUE,
    verified INTEGER DEFAULT 0
)
""")

    cur.execute("""
CREATE TABLE IF NOT EXISTS lost_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT,
    student_name TEXT,
    item_name TEXT,
    category TEXT,
    description TEXT,
    lost_date TEXT,
    lost_time TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

    cur.execute("""
CREATE TABLE IF NOT EXISTS found_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    description TEXT,
    category TEXT,
    location TEXT,
    found_date TEXT,
    found_time TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")


    conn.commit()
    conn.close()