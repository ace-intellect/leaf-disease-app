import streamlit as st
import sys
import os

# --- PATH SETUP ---
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# --- PAGE CONFIG ---
st.set_page_config(page_title="AgriDetect AI", page_icon="🌿", layout="wide")

# --- IMPORTS ---
from auth import authenticate_user, create_user
from tabs import landing

# --- GLOBAL CSS ---
def load_css():
    st.markdown("""
    <style>
    /* 1. BACKGROUND */
    .stApp {
        background-color: #0f172a; /* Dark Navy */
        color: white;
    }

    /* 2. TEXT COLORS */
    h1, h2, h3, h4, h5, p, label, div { color: white !important; }

    /* 3. INPUT FIELDS (White BG, Black Text) */
    .stTextInput input {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 1px solid #ccc !important;
        border-radius: 8px !important;
        padding: 10px 15px !important;
    }
    .stTextInput input:focus {
        border-color: #34d399 !important;
        box-shadow: none !important;
    }

    /* 4. GENERAL BUTTONS (Navigation etc) */
    div.stButton > button {
        background-color: #334155 !important;
        color: white !important;
        border: 1px solid #475569 !important;
        border-radius: 8px !important;
    }

    /* 5. FORM SUBMIT BUTTONS (Sign In / Create Account) - SPECIFIC TARGET */
    [data-testid="stFormSubmitButton"] > button {
        background-color: #475569 !important; /* Solid Slate Grey */
        color: white !important;
        border: none !important;
        font-weight: 700 !important;
        width: 100%;
        padding: 12px !important;
        margin-top: 10px !important;
        transition: background-color 0.2s;
    }
    [data-testid="stFormSubmitButton"] > button:hover {
        background-color: #64748b !important; /* Lighter Grey on Hover */
        color: white !important;
    }
    /* Fix text inside button */
    [data-testid="stFormSubmitButton"] > button p { color: white !important; }


    /* 6. CENTERED CARD CONTAINER */
    [data-testid="stForm"] {
        background-color: #1e293b; /* Slightly lighter navy */
        padding: 40px;
        border-radius: 12px;
        border: 1px solid #334155;
        max-width: 400px;
        margin: 0 auto;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    div[data-testid="stVerticalBlock"] > [style*="flex-direction: column;"] > [data-testid="stVerticalBlock"] {
        align-items: center;
    }

    /* 7. NAVBAR (Green Selected State) */
    div[data-testid="stRadio"] > div {
        background-color: rgba(255, 255, 255, 0.1);
        padding: 5px;
        border-radius: 50px;
        display: inline-flex;
        gap: 0px;
    }
    div[data-testid="stRadio"] label {
        color: #cbd5e1 !important;
        padding: 8px 20px !important;
        border-radius: 50px !important;
        border: none !important;
        background: transparent !important;
    }
    div[data-testid="stRadio"] label[data-baseweb="radio"] {
        background-color: #10b981 !important; /* Green Background */
        color: black !important;
    }
    div[data-testid="stRadio"] label[data-baseweb="radio"] p {
        color: black !important;
        font-weight: bold !important;
    }

    header {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- LOGIN PAGE ---
def show_login_page():
    if st.button("⬅ Back"):
        st.session_state['page'] = 'landing'
        st.rerun()

    st.markdown("""
    <div style="text-align: center; margin-top: 40px; margin-bottom: 20px;">
        <div style="font-size: 3rem;">🔐</div>
        <h2 style="margin: 10px 0;">Welcome Back</h2>
        <p style="color: #94a3b8 !important;">Sign in to continue</p>
    </div>
    """, unsafe_allow_html=True)

    # Centered Columns
    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        tab1, tab2 = st.tabs(["Login", "Register"])
        
        with tab1:
            with st.form("login_form"):
                user = st.text_input("Username")
                pw = st.text_input("Password", type="password")
                st.write("")
                if st.form_submit_button("Sign In"):
                    user_data = authenticate_user(user, pw)
                    if user_data:
                        st.session_state['authenticated'] = True
                        st.session_state['user'] = user_data
                        st.rerun()
                    else:
                        st.error("Invalid credentials")

        with tab2:
            with st.form("register_form"):
                new_user = st.text_input("Username")
                new_name = st.text_input("Full Name")
                new_pw = st.text_input("Password", type="password")
                st.write("")
                if st.form_submit_button("Create Account"):
                    success, msg = create_user(new_user, new_name, new_pw)
                    if success: st.success(msg)
                    else: st.error(msg)

# --- DASHBOARD ---
def show_dashboard():
    c1, c2, c3 = st.columns([2, 6, 2])
    with c1: st.markdown("### 🌿 AgriDetect")
    with c2: 
        selected_tab = st.radio("Nav", ["Home", "AI Doctor", "Analytics", "Feedback", "Profile"], horizontal=True, label_visibility="collapsed")
    with c3:
        if st.button("Logout"):
            st.session_state['authenticated'] = False
            st.session_state['page'] = 'landing'
            st.rerun()
    
    st.markdown("---")
    
    user = st.session_state.get('user', {})
    username = user.get('name', 'Farmer')

    if selected_tab == "Home": from tabs import home; home.show(username)
    elif selected_tab == "AI Doctor": from tabs import doctor; doctor.show()
    elif selected_tab == "Analytics": from tabs import analytics; analytics.show()
    elif selected_tab == "Feedback": from tabs import feedback; feedback.show()
    elif selected_tab == "Profile": from tabs import profile; profile.show(username)

# --- MAIN ---
if __name__ == "__main__":
    load_css()
    if "authenticated" not in st.session_state: st.session_state["authenticated"] = False
    if "page" not in st.session_state: st.session_state["page"] = "landing"

    if st.session_state["authenticated"]:
        show_dashboard()
    else:
        if st.session_state["page"] == "landing": landing.show()
        elif st.session_state["page"] == "login": show_login_page()