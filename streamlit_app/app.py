import streamlit as st
import os

# --- PAGE CONFIG MUST BE FIRST ---
st.set_page_config(
    page_title="Agri-AI Disease Predictor",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- IMPORTS ---
# We now import the dashboard_page here
from utils import init_db
from views import landing_page, login_page, dashboard_page, chatbot_page, profile_page
# --- INITIALIZATION ---
def init_app():
    # 1. Initialize Database
    init_db()
    
    # 2. Load Custom CSS
    # Note: We look for assets relative to where the command was run
    css_path = os.path.join("assets", "styles.css")
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        # Graceful fallback if CSS is missing
        pass 
    
    # 3. Initialize Session State Variables
    if 'authenticated' not in st.session_state:
        st.session_state['authenticated'] = False
    if 'page' not in st.session_state:
        st.session_state['page'] = 'landing'
def show_ai_assistant_button():
    st.markdown("""
    <style>
    /* Target ONLY our button using the key */
    div[data-testid="stButton"] > button {
        width: auto !important;          /* 👈 stop full width */
        min-width: unset !important;
        display: inline-flex !important; /* 👈 shrink to content */
        align-items: center;
        gap: 8px;

        position: fixed;                 /* 👈 float */
        bottom: 24px;
        right: 24px;

        background: #1DB954 !important;
        color: white !important;
        border-radius: 10px !important;
        padding: 10px 14px !important;
        font-weight: 600 !important;
        box-shadow: 0 6px 16px rgba(0,0,0,0.35);
        z-index: 9999;
    }
    </style>
    """, unsafe_allow_html=True)
    
    
# --- MAIN NAVIGATION ---
def main():
    init_app()
    # (No query-param routing) session `page` controls navigation


    if st.session_state['authenticated']:
        if st.session_state.get("page") == "chatbot":
            chatbot_page()
        elif st.session_state.get("page") == "profile":
            profile_page()
        else:
            dashboard_page()
            show_ai_assistant_button()

    else:
        if st.session_state['page'] == 'landing':
            landing_page()
        elif st.session_state['page'] == 'login':
            login_page()

if __name__ == "__main__":
    main()