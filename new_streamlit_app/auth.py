import streamlit as st
from passlib.hash import pbkdf2_sha256
from utils import run_query
from datetime import datetime

def hash_password(password):
    """Securely hashes a password."""
    return pbkdf2_sha256.hash(password)

def verify_password(password, hashed):
    """Verifies a password against its hash."""
    return pbkdf2_sha256.verify(password, hashed)

def create_user(username, name, password):
    """Registers a new user in the database."""
    # Check if user already exists
    existing_user = run_query("SELECT * FROM users WHERE username = ?", (username,))
    if existing_user:
        return False, "Username already exists!"
    
    hashed_pw = hash_password(password)
    join_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    run_query(
        "INSERT INTO users (username, name, password, join_date) VALUES (?, ?, ?, ?)",
        (username, name, hashed_pw, join_date)
    )
    return True, "Account created successfully! Please log in."

def authenticate_user(username, password):
    """Checks credentials and logs the user in."""
    user_data = run_query("SELECT * FROM users WHERE username = ?", (username,))
    
    if not user_data:
        return None  # User not found
    
    # Database columns: 0=username, 1=name, 2=password, 3=join_date
    stored_username = user_data[0][0]
    stored_name = user_data[0][1]
    stored_hash = user_data[0][2]
    stored_join_date = user_data[0][3]  # <--- THIS WAS MISSING
    
    if verify_password(password, stored_hash):
        # We now return the join_date too
        return {
            "username": stored_username, 
            "name": stored_name, 
            "join_date": stored_join_date
        }
    else:
        return None  # Wrong password

def logout():
    """Clears the session state."""
    st.session_state["authenticated"] = False
    st.session_state["user"] = None
    st.rerun()