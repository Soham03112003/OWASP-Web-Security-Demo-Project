def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS xss_comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        comment TEXT
    )
    """)

    conn.commit()
    conn.close()

# CALL IT ONCE
init_db()
