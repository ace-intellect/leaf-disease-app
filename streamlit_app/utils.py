import sqlite3
import os
from datetime import datetime
from typing import Optional

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

    # --- lightweight migrations for older DBs ---
    c.execute("PRAGMA table_info(users)")
    user_cols = {row[1] for row in (c.fetchall() or [])}
    if "join_date" not in user_cols:
        c.execute("ALTER TABLE users ADD COLUMN join_date TEXT")

    c.execute('''
        CREATE TABLE IF NOT EXISTS user_profiles (
            username TEXT PRIMARY KEY,
            role TEXT,
            email TEXT,
            phone TEXT,
            location TEXT,
            avatar_b64 TEXT,
            last_login TEXT,
            last_device TEXT,
            updated_at TEXT,
            FOREIGN KEY (username) REFERENCES users(username)
        )
    ''')

    c.execute("PRAGMA table_info(user_profiles)")
    profile_cols = {row[1] for row in (c.fetchall() or [])}
    expected_profile_cols = {
        "role",
        "email",
        "phone",
        "location",
        "avatar_b64",
        "last_login",
        "last_device",
        "updated_at",
    }
    for col in sorted(expected_profile_cols):
        if col not in profile_cols:
            c.execute(f"ALTER TABLE user_profiles ADD COLUMN {col} TEXT")

    c.execute('''
        CREATE TABLE IF NOT EXISTS analysis_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            created_at TEXT NOT NULL,
            crop_category TEXT NOT NULL,
            image_name TEXT,
            result TEXT NOT NULL,
            confidence REAL,
            upload_hash TEXT,
            FOREIGN KEY (username) REFERENCES users(username)
        )
    ''')

    c.execute('''
        CREATE UNIQUE INDEX IF NOT EXISTS idx_analysis_history_unique
        ON analysis_history(username, upload_hash, crop_category)
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS community_feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            username TEXT,
            display_name TEXT,
            category TEXT,
            crop TEXT,
            subject TEXT,
            message TEXT NOT NULL,
            rating INTEGER,
            accuracy TEXT
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

def get_user_profile(username: str):
    rows = run_query(
        "SELECT username, role, email, phone, location, avatar_b64, last_login, last_device, updated_at FROM user_profiles WHERE username = ?",
        (username,),
    )
    if not rows:
        return None
    r = rows[0]
    return {
        "username": r[0],
        "role": r[1],
        "email": r[2],
        "phone": r[3],
        "location": r[4],
        "avatar_b64": r[5],
        "last_login": r[6],
        "last_device": r[7],
        "updated_at": r[8],
    }

def upsert_user_profile(
    *,
    username: str,
    role: Optional[str] = None,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    location: Optional[str] = None,
    avatar_b64: Optional[str] = None,
    last_login: Optional[str] = None,
    last_device: Optional[str] = None,
):
    updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    run_query(
        """
        INSERT INTO user_profiles (username, role, email, phone, location, avatar_b64, last_login, last_device, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(username) DO UPDATE SET
            role = COALESCE(excluded.role, user_profiles.role),
            email = COALESCE(excluded.email, user_profiles.email),
            phone = COALESCE(excluded.phone, user_profiles.phone),
            location = COALESCE(excluded.location, user_profiles.location),
            avatar_b64 = COALESCE(excluded.avatar_b64, user_profiles.avatar_b64),
            last_login = COALESCE(excluded.last_login, user_profiles.last_login),
            last_device = COALESCE(excluded.last_device, user_profiles.last_device),
            updated_at = excluded.updated_at
        """,
        (username, role, email, phone, location, avatar_b64, last_login, last_device, updated_at),
    )

def update_user_last_login(*, username: str, device: Optional[str] = None):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    upsert_user_profile(username=username, last_login=now, last_device=device)

def get_total_scans(username: str) -> int:
    rows = run_query("SELECT COUNT(1) FROM analysis_history WHERE username = ?", (username,))
    if not rows:
        return 0
    try:
        return int(rows[0][0] or 0)
    except Exception:
        return 0

def add_analysis_history(*, username: str, crop_category: str, image_name: str, result: str, confidence: float, upload_hash: str):
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    run_query(
        "INSERT OR IGNORE INTO analysis_history (username, created_at, crop_category, image_name, result, confidence, upload_hash) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (username, created_at, crop_category, image_name, result, confidence, upload_hash),
    )

def get_analysis_history(username: str, limit: int = 200):
    rows = run_query(
        "SELECT created_at, image_name, crop_category, result, confidence FROM analysis_history WHERE username = ? ORDER BY id DESC LIMIT ?",
        (username, limit),
    )
    return rows or []

def add_community_feedback(
    *,
    username: Optional[str],
    display_name: Optional[str],
    category: Optional[str],
    crop: Optional[str],
    subject: Optional[str],
    message: str,
    rating: Optional[int],
    accuracy: Optional[str],
):
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    run_query(
        "INSERT INTO community_feedback (created_at, username, display_name, category, crop, subject, message, rating, accuracy) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (created_at, username, display_name, category, crop, subject, message, rating, accuracy),
    )

def get_recent_community_feedback(limit: int = 12):
    rows = run_query(
        "SELECT created_at, display_name, crop, subject, message, rating, accuracy FROM community_feedback ORDER BY id DESC LIMIT ?",
        (limit,),
    )
    return rows or []