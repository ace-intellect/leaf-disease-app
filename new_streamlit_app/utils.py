import sqlite3
import os
from datetime import datetime

# Path to the database file
DB_PATH = os.path.join("data", "users.db")

def init_db():
    """Initializes the SQLite database and creates the users table if it doesn't exist."""
    # Ensure data directory exists
    if not os.path.exists("data"):
        os.makedirs("data")

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Create table with fields: username, name, password (hashed), and join date
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            password TEXT NOT NULL,
            join_date TEXT
        )
    ''')
    conn.commit()
    conn.close()

def run_query(query, params=()):
    """Helper function to run a query and fetch results (if any)."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(query, params)
    
    if query.strip().upper().startswith("SELECT"):
        result = c.fetchall()
        conn.close()
        return result
    else:
        conn.commit()
        conn.close()
        return None