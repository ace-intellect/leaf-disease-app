import streamlit as st
import time
import pandas as pd
import numpy as np
import json
import os
import base64
import altair as alt
from pathlib import Path
from io import BytesIO
from PIL import Image
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime # Moved from inside the function

# Helper function to convert uploaded images for the HTML display
def image_to_base64(image):
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

# --- IMPORTS FROM OUR APP STRUCTURE ---
from auth import authenticate_user, create_user
from preprocess import preprocess_image
from model_loader import load_model, predict_image

# --- HELPER: BASE64 IMAGE LOADER ---
def get_base64(file_path):
    """Converts an image file to a base64 string for HTML embedding."""
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

# --- LANDING PAGE ---
def landing_page():
    BANNER_PATH = os.path.join("assets", "banner.png")
    bg_image_base64 = get_base64(BANNER_PATH)

    flow_images = {
        "login": os.path.join("assets", "login.png"),
        "upload": os.path.join("assets", "upload.png"),
        "ai": os.path.join("assets", "ai.png"),
        "disease": os.path.join("assets", "disease.png"),
        "insights": os.path.join("assets", "insights.png")
    }
    flow_base64 = {k: get_base64(v) for k, v in flow_images.items()}

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap');
    html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; }}

    .stApp {{
        background: linear-gradient(135deg, rgba(0,0,0,0.6), rgba(0,0,0,0.6)), 
                    url("data:image/png;base64,{bg_image_base64}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        color: white;
    }}
    header {{visibility: hidden;}}
    footer {{visibility: hidden;}}

    /* HERO & TEXT STYLES */
    .hero {{ text-align: center; padding: 5rem 1rem; animation: fadeUp 1.3s ease-in-out; }}
    .hero h1 {{ font-size: 5rem; font-weight: 900; line-height: 1.1; margin-bottom: 20px; color: white; }}
    .hero span {{ background: linear-gradient(90deg, #22d3ee, #34d399); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
    .hero p {{ font-size: 1.5rem; max-width: 800px; color: #d1fae5; margin: 0 auto 40px auto; }}

    /* BUTTONS */
    div.stButton > button {{
        background: linear-gradient(90deg, #22d3ee, #34d399) !important;
        color: #000000 !important; /* Force Black Text */
        padding: 0.8rem 3rem;
        border-radius: 999px;
        font-weight: 800;
        border: none;
        font-size: 1.2rem;
        transition: transform 0.2s;
        box-shadow: 0 0 20px rgba(52, 211, 153, 0.4);
    }}
    div.stButton > button:hover {{ transform: scale(1.05); color: #000000 !important; }}

    /* CARDS */
    .section {{ padding: 5rem 2rem; animation: fadeUp 1.2s ease-in-out; }}
    .section h2 {{ font-size: 2.8rem; font-weight: 800; margin-bottom: 45px; text-align: center; color: white; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 35px; }}
    .card {{ background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(10px); padding: 38px 34px; border-radius: 26px; border: 1px solid rgba(255,255,255,0.1); transition: all 0.4s ease; text-align: center; }}
    .card:hover {{ transform: translateY(-10px); background: rgba(255, 255, 255, 0.1); border-color: #34d399; }}
    .card h3 {{ font-size: 1.4rem; font-weight: 700; margin-bottom: 14px; color: #ecfeff; }}
    .card p {{ font-size: 1rem; line-height: 1.6; color: #99f6e4; }}

    /* FLOW */
    .flow-container {{ display: flex; flex-wrap: wrap; justify-content: center; gap: 20px; }}
    .flow-item {{ flex: 1; min-width: 150px; text-align: center; padding: 24px; background: rgba(255,255,255,0.05); border-radius: 20px; border: 1px solid rgba(255,255,255,0.05); transition: all 0.3s ease; }}
    .flow-item:hover {{ background: rgba(255,255,255,0.1); transform: translateY(-5px); border-color: #22d3ee; }}
    .flow-img {{ width: 64px; height: 64px; margin-bottom: 15px; border-radius: 12px; object-fit: cover; }}
    .flow-title {{ font-weight: 700; color: #ecfeff; }}

    .custom-footer {{ text-align: center; padding: 50px; color: #5eead4; opacity: 0.7; font-size: 0.9rem; }}
    @keyframes fadeUp {{ from {{ opacity: 0; transform: translateY(40px); }} to {{ opacity: 1; transform: translateY(0); }} }}
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="hero">
        <h1>AgriDetect<span>AI</span></h1>
        <p>An intelligent crop-health platform that detects plant diseases early, explains risks clearly, and helps farmers protect yield using AI.</p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        if st.button("Get Started / Login ➔", use_container_width=True):
            st.session_state['page'] = 'login'
            st.rerun()

    st.markdown("""
    <div class="section">
        <h2>Why AgriDetectAI?</h2>
        <div class="grid">
            <div class="card"><h3>🌾 Unified Crop Intelligence</h3><p>One unified model detects diseases across Rice, Potato, Corn, and more.</p></div>
            <div class="card"><h3>🧠 Deep Learning Accuracy</h3><p>Built on fine-tuned ResNet architectures trained on real agricultural datasets.</p></div>
            <div class="card"><h3>🔍 Explainable AI</h3><p>Visual indicators and confidence scores help you understand why a disease was detected.</p></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="section">
        <h2>How It Works</h2>
        <div class="flow-container">
            <div class="flow-item"><img src="data:image/png;base64,{flow_base64['login']}" class="flow-img"><div class="flow-title">Login</div></div>
            <div class="flow-item"><img src="data:image/png;base64,{flow_base64['upload']}" class="flow-img"><div class="flow-title">Upload Image</div></div>
            <div class="flow-item"><img src="data:image/png;base64,{flow_base64['ai']}" class="flow-img"><div class="flow-title">AI Processing</div></div>
            <div class="flow-item"><img src="data:image/png;base64,{flow_base64['disease']}" class="flow-img"><div class="flow-title">Diagnosis</div></div>
            <div class="flow-item"><img src="data:image/png;base64,{flow_base64['insights']}" class="flow-img"><div class="flow-title">Get Insights</div></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="custom-footer">© 2026 AgriDetectAI · AI for Smarter Agriculture 🌱</div>
    """, unsafe_allow_html=True)

# --- LOGIN PAGE ---
def login_page():
    BANNER_PATH = os.path.join("assets", "banner.png")
    bg_image_base64 = get_base64(BANNER_PATH)

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap');
    html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; }}

    /* BACKGROUND */
    .stApp {{
        background: linear-gradient(135deg, rgba(0,0,0,0.6), rgba(0,0,0,0.6)), 
                    url("data:image/png;base64,{bg_image_base64}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        color: white;
    }}
    header {{visibility: hidden;}}
    footer {{visibility: hidden;}}

    /* GLASS LOGIN CARD */
    .login-card {{
        background: rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(12px);
        padding: 40px;
        border-radius: 24px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        text-align: center;
        margin-bottom: 20px;
        animation: fadeUp 0.8s ease-out;
    }}
    
    .login-title {{
        font-size: 2.2rem;
        font-weight: 800;
        margin-bottom: 10px;
        background: linear-gradient(90deg, #22d3ee, #34d399);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }}

    /* INPUT FIELDS STYLING */
    .stTextInput input {{
        background-color: rgba(0, 0, 0, 0.3) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 12px !important;
        padding: 12px !important;
    }}
    .stTextInput input:focus {{
        border-color: #22d3ee !important;
        box-shadow: 0 0 10px rgba(34, 211, 238, 0.3) !important;
    }}
    .stTextInput label {{
        color: #d1fae5 !important;
        font-weight: 600;
    }}

    /* TABS STYLING */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 10px;
        background-color: rgba(0,0,0,0.3);
        padding: 10px;
        border-radius: 50px;
        justify-content: center;
    }}
    .stTabs [data-baseweb="tab"] {{
        height: 40px;
        border-radius: 40px;
        color: white;
        background-color: transparent;
        border: none;
        flex: 1;
    }}
    .stTabs [aria-selected="true"] {{
        background-color: #34d399 !important;
        color: black !important;
        font-weight: bold;
    }}

    /* --- FIX: TARGET MAIN FORM BUTTONS SPECIFICALLY (Prevents Eye Icon distortion) --- */
    /* This prevents the style from hitting the 'eye' icon button inside the input */
    div[data-testid="stFormSubmitButton"] button {{
        width: 100%;
        background: linear-gradient(90deg, #22d3ee, #34d399) !important;
        color: #000000 !important; /* Forces Black Text */
        padding: 0.8rem;
        border-radius: 12px;
        font-weight: 800;
        border: none;
        margin-top: 10px;
    }}
    
    div[data-testid="stFormSubmitButton"] button:hover {{
        transform: scale(1.02);
        box-shadow: 0 0 15px rgba(52, 211, 153, 0.5);
        color: #000000 !important;
    }}

    /* BACK BUTTON STYLING (Outside Form) */
    div.stButton > button {{
        background: rgba(255,255,255,0.1);
        color: white;
        border: 1px solid rgba(255,255,255,0.2);
    }}

    @keyframes fadeUp {{ from {{ opacity: 0; transform: translateY(20px); }} to {{ opacity: 1; transform: translateY(0); }} }}
    </style>
    """, unsafe_allow_html=True)

    # --- LAYOUT ---
    c1, c2, c3 = st.columns([1, 1.5, 1])
    
    with c2:
        st.markdown('<div class="login-card"><div class="login-title">Welcome Back! 👋</div><p style="color:#d1fae5;">Access your intelligent crop dashboard</p></div>', unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["Login", "Register"])
        
        with tab1:
            with st.form("login_form"):
                username = st.text_input("Username", placeholder="Enter your username")
                password = st.text_input("Password", type="password", placeholder="Enter your password")
                if st.form_submit_button("Log In"):
                    user = authenticate_user(username, password)
                    if user:
                        st.success(f"Welcome, {user['name']}!")
                        time.sleep(1)
                        st.session_state['authenticated'] = True
                        st.session_state['user'] = user
                        st.rerun()
                    else:
                        st.error("Invalid credentials.")

        with tab2:
            with st.form("register_form"):
                new_user = st.text_input("Choose a Username")
                new_name = st.text_input("Your Full Name")
                new_pass = st.text_input("Choose a Password", type="password")
                confirm_pass = st.text_input("Confirm Password", type="password")
                if st.form_submit_button("Create Account"):
                    if new_pass != confirm_pass:
                        st.error("Passwords do not match!")
                    elif not new_user or not new_pass:
                        st.error("Please fill in all fields.")
                    else:
                        success, msg = create_user(new_user, new_name, new_pass)
                        if success: st.success(msg)
                        else: st.error(msg)
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("⬅ Back to Home"):
            st.session_state['page'] = 'landing'
            st.rerun()

# --- DASHBOARD PAGE ---
# --- DASHBOARD PAGE ---
# --- DASHBOARD PAGE ---
def dashboard_page():
    BANNER_PATH = os.path.join("assets", "banner.png")
    bg_image_base64 = get_base64(BANNER_PATH)
    
    user = st.session_state['user']

    # --- CSS ---
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Inter', sans-serif;
    }}

    .stApp {{
        background: linear-gradient(135deg, rgba(0,0,0,0.75), rgba(0,0,0,0.9)), 
                    url("data:image/png;base64,{bg_image_base64}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        color: white;
    }}

    header {{visibility:hidden;}}
    footer {{visibility:hidden;}}

    /* Title Styling */
    h1 {{
        font-weight: 900;
        font-size: 3rem;
        letter-spacing: -1px;
        margin: 0 !important;
        padding: 0 !important;
    }}

    /* --- PILL NAVBAR STYLE --- */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 10px;
        background-color: rgba(255, 255, 255, 0.05); /* Glass Container */
        padding: 10px 20px;
        border-radius: 50px;
        justify-content: center;
        flex-wrap: wrap; /* Allow wrapping on mobile */
        margin-bottom: 20px;
    }}

    .stTabs [data-baseweb="tab"] {{
        height: 40px;
        border-radius: 40px;
        color: #e2e8f0 !important; /* Unselected Text Color */
        background-color: transparent;
        border: none;
        font-weight: 600;
        font-size: 0.95rem;
        padding: 0 20px; /* Padding for pill width */
    }}

    .stTabs [aria-selected="true"] {{
        background-color: #34d399 !important; /* Green Active Background */
        color: #020617 !important; /* Dark Text */
        font-weight: 800;
        box-shadow: 0 4px 15px rgba(52, 211, 153, 0.4);
    }}

    /* UI ELEMENTS */
    [data-testid="stFileUploader"] {{
        width:100% !important;
        padding:2.2rem !important;
        border-radius:20px;
        border:1px dashed rgba(52,211,153,0.7);
        background:rgba(255,255,255,0.05);
    }}

    /* BUTTON STYLES */
    div.stButton > button {{
        background: linear-gradient(90deg, #22d3ee, #34d399) !important;
        color: #000000 !important;
        font-weight: 800 !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.6rem 1.2rem !important;
        transition: all 0.3s ease !important;
    }}
    div.stButton > button:hover {{
        transform: scale(1.02) !important;
        box-shadow: 0 0 15px rgba(52, 211, 153, 0.5) !important;
        color: #000000 !important;
    }}
    div.stButton > button p {{
        color: #000000 !important;
        font-weight: 800 !important;
    }}

    .stSelectbox div[data-baseweb="select"] > div {{
        background-color: rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
    }}
    
    div[data-baseweb="popover"] ul {{
        background-color: #1a1a1a !important;
    }}
    </style>
    """, unsafe_allow_html=True)

    # --- SIDEBAR ---
    with st.sidebar:
        if os.path.exists("assets/logo.png"):
            st.image("assets/logo.png", width=120)
        st.markdown(f"## 👨‍🌾 {user['name']}")
        if user.get('join_date'):
            st.caption(f"Member since: {user['join_date'].split(' ')[0]}")
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            from auth import logout
            logout()

    # --- MAIN HEADER (Fixed Alignment) ---
    # We put the Title and the Logout button in the same row so they are side-by-side
    c_header, c_logout = st.columns([8, 1])
    
    with c_header:
        # Using markdown for title allows better control over margins
        st.markdown("<h1 style='padding-top: 10px;'>🌿 AgriDetectAI Dashboard</h1>", unsafe_allow_html=True)
    
    with c_logout:
        st.write("") # Spacer to push button down slightly
        if st.button("🚪", help="Logout"):
            st.session_state['authenticated'] = False
            st.session_state['user'] = None
            st.session_state['page'] = 'landing'
            st.rerun()

    tab_home, tab_profile, tab_analysis, tab_connect, tab_climate, tab_analytics, tab_history, tab_about = st.tabs([
        "🏠 Home", "👤 Profile", "🔍 Analysis", "🤝 AgriConnect", "🌦️ Climate", "📊 Analytics", "📜 History", "ℹ️ About"
    ])

    # =====================================================
    # 🏠 HOME TAB (Updated with Meaningful Text)
    # =====================================================
    with tab_home:
        from datetime import datetime
        today_date = datetime.now().strftime("%A, %d %B %Y")
        
        # --- 1. CUSTOM CSS FOR THIS TAB ---
        st.markdown("""
        <style>
        .section-title {
            font-size: 1.8rem;
            font-weight: 800;
            margin-top: 40px;
            margin-bottom: 20px;
            background: linear-gradient(90deg, #34d399, #22d3ee);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .stat-card {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 20px;
            text-align: center;
            transition: transform 0.3s;
        }
        .stat-card:hover {
            transform: translateY(-5px);
            background: rgba(255, 255, 255, 0.1);
            border-color: #34d399;
        }
        .stat-number {
            font-size: 2.5rem;
            font-weight: 900;
            color: white;
        }
        .stat-label {
            color: #cbd5e1;
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .review-card {
            background: rgba(20, 20, 30, 0.6);
            border-left: 4px solid #34d399;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .review-text {
            font-style: italic;
            color: #e2e8f0;
            font-size: 1rem;
            line-height: 1.6;
        }
        .review-author {
            margin-top: 15px;
            font-weight: bold;
            color: #34d399;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .custom-footer {
            margin-top: 80px;
            padding-top: 40px;
            border-top: 1px solid rgba(255,255,255,0.1);
            text-align: center;
            color: #94a3b8;
        }
        .footer-links a {
            color: #94a3b8;
            margin: 0 10px;
            text-decoration: none;
            font-size: 0.9rem;
            transition: color 0.3s;
        }
        .footer-links a:hover {
            color: #34d399;
        }
        </style>
        """, unsafe_allow_html=True)

        # --- 2. FARM OVERVIEW HERO (NEW CONTENT) ---
        st.markdown(f"""
        <div style="padding: 20px 0;">
            <h1 style='font-size: 3rem; margin-bottom: 10px; color: white;'>Farm Overview & Daily Insights</h1>
            <p style='color: #34d399; font-size: 1.1rem; font-weight: 600; margin-bottom: 15px; letter-spacing: 0.5px;'>
                📅 {today_date} &nbsp; | &nbsp; 📍 Nalgonda, Telangana
            </p>
            <p style='color: #cbd5e1; font-size: 1.15rem; line-height: 1.6; max-width: 900px;'>
                Welcome to your command center. You are currently monitoring <b>12 acres</b> of active cultivation for the 
                <b>Rabi Season</b>. Our AI systems have detected optimal humidity levels for Rice, but please review the 
                <b>3 active alerts</b> regarding Potato Blight in Sector 4. Use the tabs above to run new diagnostics or check soil analytics.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")

        # --- 3. LIVE STATUS ---
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("""
            <div class="stat-card" style="display: flex; align-items: center; justify-content: space-between;">
                <div style="text-align: left;">
                    <h3 style="margin:0;">🌾 Active Crops</h3>
                    <p style="color: #cbd5e1; margin:0;">Rice (Sona Masoori), Potato</p>
                </div>
                <div style="font-size: 2.5rem;">🚜</div>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown("""
            <div class="stat-card" style="display: flex; align-items: center; justify-content: space-between; border-color: #34d399;">
                <div style="text-align: left;">
                    <h3 style="margin:0; color: #34d399;">🛡️ System Status</h3>
                    <p style="color: #cbd5e1; margin:0;">AI Model Online & Ready</p>
                </div>
                <div style="font-size: 2.5rem;">✅</div>
            </div>
            """, unsafe_allow_html=True)

        # --- 4. IMPACT STATS ---
        st.markdown('<div class="section-title">🚀 Our Impact</div>', unsafe_allow_html=True)
        ac1, ac2, ac3, ac4 = st.columns(4)
        with ac1:
            st.markdown('<div class="stat-card"><div class="stat-number">15k+</div><div class="stat-label">Scans Performed</div></div>', unsafe_allow_html=True)
        with ac2:
            st.markdown('<div class="stat-card"><div class="stat-number">96%</div><div class="stat-label">Accuracy Rate</div></div>', unsafe_allow_html=True)
        with ac3:
            st.markdown('<div class="stat-card"><div class="stat-number">50+</div><div class="stat-label">Villages Covered</div></div>', unsafe_allow_html=True)
        with ac4:
            st.markdown('<div class="stat-card"><div class="stat-number">24/7</div><div class="stat-label">Expert Support</div></div>', unsafe_allow_html=True)

        # --- 5. REVIEWS ---
        st.markdown('<div class="section-title">💬 What Farmers Say</div>', unsafe_allow_html=True)
        rc1, rc2 = st.columns(2)
        with rc1:
            st.markdown("""
            <div class="review-card"><div class="review-text">"I used to lose 30% of my potato crop to Blight every year. AgriDetect diagnosed it early!"</div><div class="review-author">👤 Ramesh Reddy <span style="font-weight:normal; color:#64748b;">(Warangal)</span></div></div>
            <div class="review-card"><div class="review-text">"Simple interface, even my father can use it. Telugu support would be great!"</div><div class="review-author">👤 Sita Lakshmi <span style="font-weight:normal; color:#64748b;">(Karimnagar)</span></div></div>
            """, unsafe_allow_html=True)
        with rc2:
            st.markdown("""
            <div class="review-card"><div class="review-text">"Government schemes section is very helpful. Checked my eligibility instantly."</div><div class="review-author">👤 Krishna Rao <span style="font-weight:normal; color:#64748b;">(Nalgonda)</span></div></div>
            <div class="review-card"><div class="review-text">"Best app for Rice Blast detection. Chemical dosage recommendations are accurate."</div><div class="review-author">👤 Venkat Goud <span style="font-weight:normal; color:#64748b;">(Khammam)</span></div></div>
            """, unsafe_allow_html=True)

        # --- 6. FOOTER ---
        st.markdown("""
        <div class="custom-footer">
            <div style="font-size: 1.5rem; font-weight: 800; margin-bottom: 20px;">AgriDetect<span style="color: #34d399;">AI</span></div>
            <div class="footer-links"><a href="#">About Us</a><a href="#">Privacy Policy</a><a href="#">Terms</a><a href="#">Contact</a></div>
            <p style="margin-top: 30px; font-size: 0.8rem; opacity: 0.6;">© 2026 AgriDetectAI · AI for Smarter Agriculture 🌱 <br> Designed with ❤️ for Indian Farmers.</p>
        </div>
        """, unsafe_allow_html=True)

    # =====================================================
    # 👤 PROFILE TAB (No Changes)
    # =====================================================
    with tab_profile:
        user_data = st.session_state.get('user', user)
        real_fullname = user_data.get('name', 'Farmer')
        join_date_raw = str(user_data.get('created_at', '2026-01-01'))
        real_join_date = join_date_raw.split(' ')[0]

        st.markdown("""
        <style>
        [data-testid="stFileUploader"] button {
            background: linear-gradient(90deg, #22d3ee, #34d399) !important;
            color: #020617 !important;
            font-weight: 800 !important;
            border: none !important;
            padding: 8px 20px !important;
            border-radius: 8px !important;
        }
        [data-testid="stFileUploader"] section {
            background-color: rgba(255, 255, 255, 0.05);
            border: 2px dashed rgba(52, 211, 153, 0.5);
            border-radius: 15px;
            padding: 20px;
            text-align: center;
        }
        .stTextInput input, .stSelectbox div[data-baseweb="select"] > div {
            background-color: rgba(255, 255, 255, 0.9) !important;
            color: black !important;
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
            border-radius: 8px !important;
        }
        .profile-card {
            background: linear-gradient(135deg, rgba(255, 255, 255, 0.1), rgba(255, 255, 255, 0.05));
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 24px;
            padding: 40px 20px;
            text-align: center;
            box-shadow: 0 20px 40px rgba(0,0,0,0.3);
        }
        .avatar-circle {
            width: 140px; height: 140px; margin: 0 auto 20px auto;
            background: linear-gradient(135deg, #34d399, #22d3ee);
            border-radius: 50%; display: flex; align-items: center; justify-content: center;
            font-size: 4rem; border: 4px solid rgba(255,255,255,0.2); overflow: hidden;
        }
        .avatar-img { width: 100%; height: 100%; object-fit: cover; }
        </style>
        """, unsafe_allow_html=True)

        st.markdown("<h1 style='margin-bottom: 10px;'>👤 My <span style='color:#34d399'>Profile</span></h1>", unsafe_allow_html=True)
        c1, c2 = st.columns([1, 2], gap="large")

        with c1:
            uploaded_avatar = st.file_uploader("Change Picture", type=['jpg', 'png', 'jpeg'], label_visibility="collapsed")
            inner_avatar_html = "👨‍🌾"
            if uploaded_avatar is not None:
                image = Image.open(uploaded_avatar)
                img_b64 = image_to_base64(image)
                inner_avatar_html = f'<img src="data:image/png;base64,{img_b64}" class="avatar-img">'

            st.markdown(f"""
            <div class="profile-card">
                <div style="background: #fbbf24; color: #020617; padding: 6px 16px; border-radius: 50px; font-size: 0.75rem; font-weight: 800; display: inline-block; margin-bottom: 15px;">PRO MEMBER</div>
                <div class="avatar-circle">{inner_avatar_html}</div>
                <h2 style="margin:0; color: white; font-weight: 800;">{real_fullname}</h2>
                <p style="color: #94a3b8; font-size: 0.95rem;">Precision Farmer</p>
                <p style="color: #cbd5e1; margin-top: 25px; font-size: 0.9rem; line-height: 1.6;"><b>Joined:</b> {real_join_date}<br><b>Location:</b> Nalgonda, TG</p>
            </div>
            """, unsafe_allow_html=True)

        with c2:
            with st.container():
                st.markdown("### ⚙️ Account Details")
                col_form1, col_form2 = st.columns(2)
                with col_form1:
                    new_name = st.text_input("Full Name", value=real_fullname)
                    user_handle = user_data.get('username', 'farmer')
                    email = st.text_input("Email", value=f"{user_handle}@agridetect.com", disabled=True)
                with col_form2:
                    phone = st.text_input("Phone Number", value="+91 98765 43210")
                    lang = st.selectbox("App Language", ["English", "Telugu (తెలుగు)", "Hindi (हिंदी)"])

                st.markdown("---")
                st.markdown("#### 🔔 Notification Preferences")
                c_t1, c_t2 = st.columns(2)
                with c_t1: st.toggle("Email Alerts", value=True)
                with c_t2: st.toggle("Share Analytics", value=False)
                
                st.write("")
                b1, b2 = st.columns([1, 1])
                with b1:
                    if st.button("💾 Save Changes"):
                        if 'user' in st.session_state:
                            st.session_state['user']['name'] = new_name
                        st.toast("Profile updated successfully!", icon="✅")
                        st.rerun()
                with b2: 
                    st.button("🔑 Change Password")

    # =====================================================
    # 🔍 ANALYSIS TAB (No Changes)
    # =====================================================
    with tab_analysis:
        st.markdown("### AI Disease Diagnosis")
        config_path = os.path.join("config", "model_config.json")

        if not os.path.exists(config_path):
            st.error("Config file not found!")
            return

        with open(config_path) as f:
            config = json.load(f)

        model_options = {
            "Rice & Potato": "rice_potato",
            "Corn & Blackgram": "corn_blackgram"
        }
        
        col_select, _ = st.columns([2, 2])
        with col_select:
            selected_display_name = st.selectbox("🎯 Select Crop Category", options=list(model_options.keys()))
        selected_model_name = model_options[selected_display_name]

        st.markdown("---")
        left, center, right = st.columns([1,6,1])

        with center:
            st.info(f"📸 Upload a clear leaf image for {selected_display_name}")
            uploaded_file = st.file_uploader("🌿 Upload Leaf Image — JPG / PNG (Max 5MB)", type=["jpg","jpeg","png"])

        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            col1, col2 = st.columns([1,1.5])

            with col1:
                st.image(image, caption='Your Upload', use_container_width=True)

            with col2:
                st.markdown("#### 🔬 Diagnosis Report")
                with st.spinner('Scanning leaf tissues...'):
                    model, model_type = load_model(selected_model_name)
                    if not model:
                        st.error("Model failed to load.")
                        return

                    processed_img = preprocess_image(image, model_type=model_type, model_key=selected_model_name)

                    try:
                        predictions = predict_image(model, model_type, processed_img)
                        class_indices = config['models'][selected_model_name]['classes']
                        predicted_class_index = np.argmax(predictions)
                        confidence = np.max(predictions) * 100

                        predicted_label = class_indices.get(str(predicted_class_index), f"Class {predicted_class_index}")

                        if "healthy" in predicted_label.lower():
                            st.success(f"**Status: {predicted_label.upper()}**")
                            st.balloons()
                        else:
                            st.error(f"**Detected: {predicted_label.upper()}**")

                        st.caption(f"Confidence: {confidence:.2f}%")
                        st.progress(int(confidence))

                        probs = predictions[0]
                        df_chart = pd.DataFrame({
                            "Condition": [class_indices.get(str(i), f"Class {i}") for i in range(len(probs))],
                            "Confidence": probs
                        }).sort_values(by="Confidence", ascending=False)

                        chart = alt.Chart(df_chart).mark_bar(cornerRadiusEnd=6).encode(
                            x=alt.X('Confidence:Q', title=None, axis=alt.Axis(format='%')),
                            y=alt.Y('Condition:N', sort='-x', title=None),
                            color=alt.Color('Confidence:Q', scale=alt.Scale(scheme="blues"), legend=None),
                            tooltip=[alt.Tooltip('Condition:N'), alt.Tooltip('Confidence:Q', format='.2%')]
                        ).properties(height=350)

                        text = chart.mark_text(align='left', baseline='middle', dx=5).encode(
                            text=alt.Text('Confidence:Q', format='.1%')
                        )

                        st.altair_chart(chart + text, use_container_width=True)

                    except Exception as e:
                        st.error(f"Prediction Error: {e}")

    # =====================================================
    # 🤝 AGRICONNECT TAB (No Changes)
    # =====================================================
    with tab_connect:
        root_dir = os.getcwd()
        feedback_dir = os.path.join(root_dir, "data")
        feedback_file = os.path.join(feedback_dir, "feedback_log.txt")
        os.makedirs(feedback_dir, exist_ok=True)

        st.markdown("""
        <style>
        .feedback-card {
            background: rgba(0, 0, 0, 0.2);
            border-left: 4px solid #34d399;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 15px;
        }
        .user-name { color: #34d399 !important; font-weight: bold; }
        .feedback-text { color: #e2e8f0 !important; font-style: italic; }
        </style>
        """, unsafe_allow_html=True)

        st.markdown("<h1 style='text-align: center;'>💬 Community <span style='color:#34d399'>Feedback</span></h1>", unsafe_allow_html=True)
        c1, c2 = st.columns([1.5, 1], gap="large")

        with c1:
            with st.form("user_feedback"):
                st.markdown("### 📝 Submit Your Review")
                st.radio("Hidden Label", ["🌱 Accuracy", "🐛 Bug", "💡 Feature", "❤️ Other"], horizontal=True, label_visibility="collapsed")
                col_in1, col_in2 = st.columns(2)
                with col_in1: st.text_input("Your Name (Optional)")
                with col_in2: st.selectbox("Related Crop", ["General", "Rice", "Potato", "Corn", "Blackgram", "Cotton", "Tomato", "Pumpkin", "Wheat",])
                st.text_input("Subject")
                message = st.text_area("Detailed Feedback", height=120)
                
                c_r1, c_r2 = st.columns(2)
                with c_r1: st.slider("Rate Us", 1, 5, 5)
                with c_r2: st.radio("AI Accuracy", ["Yes, Spot on! ✅", "Partially ⚠️", "No, Incorrect ❌"], horizontal=True)

                if st.form_submit_button("🚀 Submit Feedback"):
                    if message: st.success("✅ Thank you!"); st.balloons()
                    else: st.warning("Please enter a message.")

        with c2:
            st.markdown("### 🌍 Recent Activity")
            st.markdown("""
            <div class="feedback-card"><div class="user-name">Venkatesh K.</div><div class="feedback-text">"Rice Blast detection saved my crop!"</div></div>
            <div class="feedback-card"><div class="user-name">Sarah Jenkins</div><div class="feedback-text">"Great accuracy on Potato Late Blight."</div></div>
            """, unsafe_allow_html=True)

    # =====================================================
    # 🌦️ CLIMATE TAB (No Changes)
    # =====================================================
    with tab_climate:
        st.header("🌦️ Local Climate & Alerts")
        col1, col2, col3 = st.columns(3)
        with col1: st.metric(label="Temperature", value="28°C", delta="1.2°C")
        with col2: st.metric(label="Humidity", value="65%", delta="-5%")
        with col3: st.metric(label="Wind Speed", value="12 km/h", delta="Normal")
            
        st.markdown("---")
        st.subheader("⚠️ Active Disease Alerts")
        st.warning("**High Risk Alert: Rice Blast**\n\n**Cause:** High humidity (>90%) and lower night temperatures.\n\n**Action:** Monitor fields closely.")
        st.info("**Moderate Risk: Potato Late Blight**\n\n**Cause:** Intermittent rains predicted.")

    # =====================================================
    # 📊 ANALYTICS TAB (No Changes)
    # =====================================================
    with tab_analytics:
        st.markdown("""
        <style>
        .kpi-card { 
            background: rgba(255, 255, 255, 0.05); 
            backdrop-filter: blur(10px); 
            border-radius: 15px; 
            padding: 20px; 
            border: 1px solid rgba(255, 255, 255, 0.1); 
            text-align: center; 
        }
        .kpi-value { font-size: 2.2rem; font-weight: 800; color: white; margin: 0; }
        .kpi-label { color: #cbd5e1; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1px; }
        .chart-container { background: rgba(0, 0, 0, 0.2); border-radius: 20px; padding: 20px; border: 1px solid rgba(255, 255, 255, 0.05); }
        .report-table { width: 100%; border-collapse: collapse; color: #e2e8f0; font-size: 0.9rem; }
        .report-table th { text-align: left; padding: 15px; border-bottom: 1px solid rgba(255,255,255,0.1); color: #34d399; text-transform: uppercase; font-size: 0.8rem; }
        .report-table td { padding: 15px; border-bottom: 1px solid rgba(255,255,255,0.05); }
        .status-badge { padding: 5px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: bold; }
        .status-high { background: rgba(248, 113, 113, 0.2); color: #f87171; }
        .status-safe { background: rgba(52, 211, 153, 0.2); color: #34d399; }
        </style>
        """, unsafe_allow_html=True)

        st.markdown("<h1 style='text-align: center;'>📊 Farm <span style='color:#34d399'>Analytics</span></h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #cbd5e1; margin-bottom: 30px;'>Real-time insights on crop health and yield predictions.</p>", unsafe_allow_html=True)

        k1, k2, k3, k4 = st.columns(4)
        with k1: st.markdown('<div class="kpi-card"><div class="kpi-label">Total Scans</div><div class="kpi-value">1,248</div></div>', unsafe_allow_html=True)
        with k2: st.markdown('<div class="kpi-card"><div class="kpi-label">Avg Health</div><div class="kpi-value">87%</div></div>', unsafe_allow_html=True)
        with k3: st.markdown('<div class="kpi-card"><div class="kpi-label">Alerts</div><div class="kpi-value" style="color: #f87171;">14</div></div>', unsafe_allow_html=True)
        with k4: st.markdown('<div class="kpi-card"><div class="kpi-label">Est. Yield</div><div class="kpi-value">4.2T</div></div>', unsafe_allow_html=True)

        st.write("") 
        yield_data = pd.DataFrame({"Crop": ["Rice", "Potato", "Wheat", "Tomato"], "Yield (Tons)": [45, 60, 30, 25]})
        trend_data = pd.DataFrame({"Month": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"], "Healthy": [80, 85, 82, 88, 90, 87], "Diseased": [20, 15, 18, 12, 10, 13]})

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("### 🌾 Crop Yield Forecast")
            fig_yield = px.bar(yield_data, x="Crop", y="Yield (Tons)", color="Crop", color_discrete_sequence=["#34d399", "#22d3ee", "#fbbf24", "#f87171"])
            fig_yield.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(255, 255, 255, 0.05)", font=dict(color="white"), showlegend=False, margin=dict(l=20, r=20, t=20, b=20))
            st.plotly_chart(fig_yield, use_container_width=True)

        with c2:
            st.markdown("### 📉 Disease Trends")
            fig_trend = go.Figure()
            fig_trend.add_trace(go.Scatter(x=trend_data["Month"], y=trend_data["Healthy"], fill='tozeroy', mode='lines', name='Healthy', line=dict(width=3, color='#34d399')))
            fig_trend.add_trace(go.Scatter(x=trend_data["Month"], y=trend_data["Diseased"], fill='tozeroy', mode='lines', name='Diseased', line=dict(width=3, color='#f87171')))
            fig_trend.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(255, 255, 255, 0.05)", font=dict(color="white"), legend=dict(orientation="h", y=1.1), margin=dict(l=20, r=20, t=20, b=20))
            st.plotly_chart(fig_trend, use_container_width=True)

        st.markdown("### 📋 Recent Field Reports")
        st.markdown("""
        <div class="chart-container">
            <table class="report-table">
                <thead><tr><th>Scan ID</th><th>Date</th><th>Crop</th><th>Diagnosis</th><th>Risk Level</th></tr></thead>
                <tbody>
                    <tr><td>#SC-2045</td><td>Feb 24, 2026</td><td>Potato</td><td>Early Blight</td><td><span class="status-badge status-high">High Risk</span></td></tr>
                    <tr><td>#SC-2044</td><td>Feb 23, 2026</td><td>Rice</td><td>Healthy</td><td><span class="status-badge status-safe">Safe</span></td></tr>
                </tbody>
            </table>
        </div>
        """, unsafe_allow_html=True)

    # =====================================================
    # 📜 HISTORY TAB (No Changes)
    # =====================================================
    with tab_history:
        st.header("📜 Analysis History")
        st.dataframe(pd.DataFrame({
            "Date": ["2023-10-01", "2023-10-05", "2023-10-12"],
            "Image": ["IMG_2022.jpg", "IMG_2025.jpg", "IMG_2030.jpg"],
            "Result": ["Healthy", "Rice Blast", "Healthy"],
            "Confidence": ["99%", "87%", "95%"]
        }))

    # =====================================================
    # ℹ️ ABOUT TAB (No Changes)
    # =====================================================
    with tab_about:
        st.header("ℹ️ About Agri-AI")
        st.markdown("""
        **Agri-AI** is a cutting-edge leaf disease detection platform...
        ### 🧠 The Engine
        * **📸 Image-based leaf disease detection**
        * **🤖 Deep Learning models**
        * **🌾 Support for multiple crops**
        
        ### 🌿 AI Models
        AgriDetectAI leverages a **multi-model architecture**...
        - **Rice & Potato**
        - **Corn & Blackgram**
        - **Cotton & Tomato**
        - **Pumpkin & Wheat**
        """)