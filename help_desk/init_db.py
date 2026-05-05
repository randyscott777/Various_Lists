import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'helpdesk.db')
conn = sqlite3.connect(db_path)
conn.execute('''
    CREATE TABLE IF NOT EXISTS tickets (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        title       TEXT NOT NULL,
        description TEXT,
        category    TEXT,
        priority    TEXT,
        status      TEXT DEFAULT 'Open',
        assigned_to TEXT,
        created_at  TEXT,
        updated_at  TEXT
    )
''')
conn.commit()
conn.close()
print("Database initialized: helpdesk.db")
