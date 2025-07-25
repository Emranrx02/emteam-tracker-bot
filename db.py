import sqlite3
from datetime import datetime, timedelta


def init_db():
    conn = sqlite3.connect("messages.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            user_id INTEGER,
            username TEXT,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()


def log_message(user_id, username):
    conn = sqlite3.connect("messages.db")
    c = conn.cursor()
    c.execute(
        "INSERT INTO messages (user_id, username, timestamp) VALUES (?, ?, ?)",
        (user_id, username, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()


def get_total_messages(username):
    conn = sqlite3.connect("messages.db")
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM messages WHERE username = ?", (username, ))
    count = c.fetchone()[0]
    conn.close()
    return count


def get_24h_messages(username):
    conn = sqlite3.connect("messages.db")
    c = conn.cursor()
    since = datetime.utcnow() - timedelta(days=1)
    c.execute(
        "SELECT COUNT(*) FROM messages WHERE username = ? AND timestamp >= ?",
        (username, since.isoformat()))
    count = c.fetchone()[0]
    conn.close()
    return count
