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
from views import landing_page, login_page, dashboard_page


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

# --- MAIN NAVIGATION ---
def main():
    init_app()
    
    # A. If Authenticated -> Show The Real Dashboard
    if st.session_state['authenticated']:
        dashboard_page()
        
    # B. If Not Authenticated -> Show Landing or Login
    else:
        if st.session_state['page'] == 'landing':
            landing_page()
        elif st.session_state['page'] == 'login':
            login_page()

if __name__ == "__main__":
    main()