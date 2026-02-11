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
import hashlib
from dotenv import load_dotenv
import google.generativeai as genai


# Helper function to convert uploaded images for the HTML display
def image_to_base64(image):
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

# --- IMPORTS FROM OUR APP STRUCTURE ---
from auth import authenticate_user, create_user
from preprocess import preprocess_image
from model_loader import load_model, predict_image
from utils import add_analysis_history, get_analysis_history, add_community_feedback, get_recent_community_feedback
from utils import get_user_profile, upsert_user_profile, update_user_last_login, get_total_scans, run_query

load_dotenv()

def _get_gemini_model_name():
    model_name = None
    try:
        for m in genai.list_models():
            if "generateContent" in getattr(m, "supported_generation_methods", []):
                model_name = m.name
                break
    except Exception:
        model_name = None
    return model_name or "models/gemini-pro"

def generate_treatment_prevention(*, crop_category: str, disease_label: str):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY not configured")

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(_get_gemini_model_name())

    prompt = (
        "You are an agricultural extension assistant. "
        "Provide farmer-safe advice. "
        "Return Markdown only.\n\n"
        f"Crop category: {crop_category}\n"
        f"Detected disease/condition: {disease_label}\n\n"
        "Write two sections with headings:\n"
        "## Treatment\n"
        "- Give practical steps\n"
        "- Mention cultural practices first, then chemical options if needed\n"
        "- Include safety notes (PPE, follow label, local regulations)\n\n"
        "## Prevention\n"
        "- Give preventive steps for next time\n\n"
        "Keep it concise. If the disease name is ambiguous, say so and give general best-practice guidance."
    )

    response = model.generate_content(prompt)
    text = response.text if response and getattr(response, "text", None) else ""
    if not text.strip():
        raise RuntimeError("Gemini returned empty response")
    return text

# --- HELPER: BASE64 IMAGE LOADER ---
def get_base64(file_path):
    """Converts an image file to a base64 string for HTML embedding."""
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""


def render_profile_panel(user_data):
    """Render the profile panel (moved from the Profile tab)."""
    # (No top-right close icon here — navigation uses Back button)

    user_data = user_data or {}
    username = user_data.get("username")
    profile = get_user_profile(username) if username else None
    profile = profile or {}

    real_fullname = user_data.get("name") or "Farmer"
    join_date_raw = str(user_data.get("join_date") or "2026-01-01")
    real_join_date = join_date_raw.split(" ")[0]

    role_options = {
        "farmer": "🌾 Farmer",
        "student": "🎓 Agri Student",
        "researcher": "🧪 Researcher",
        "consultant": "🏢 Agri Consultant",
    }
    role_key = (profile.get("role") or "farmer").lower().strip()
    if role_key not in role_options:
        role_key = "farmer"
    role_label = role_options[role_key]

    last_login_display = (profile.get("last_login") or "—").split(" ")[0] if profile.get("last_login") else "—"
    last_device_display = profile.get("last_device") or "—"
    location_value = profile.get("location") or "—"

    st.markdown("""
    <style>
    /* UPLOAD BUTTON STYLING */
    [data-testid="stFileUploader"] button {
        background: linear-gradient(90deg, #22d3ee, #34d399) !important;
        color: #020617 !important;
        font-weight: 800 !important;
        border: none !important;
        padding: 8px 20px !important;
        border-radius: 8px !important;
    }
    [data-testid="stFileUploader"] button:hover {
        transform: scale(1.02) !important;
        box-shadow: 0 0 15px rgba(52, 211, 153, 0.5) !important;
    }
    [data-testid="stFileUploader"] { color: white !important; }
    [data-testid="stFileUploader"] small { color: #e2e8f0 !important; }
    [data-testid="stFileUploader"] span { color: white !important; }
    
    [data-testid="stFileUploader"] section {
        background-color: rgba(255, 255, 255, 0.05);
        border: 2px dashed rgba(52, 211, 153, 0.5);
        border-radius: 15px;
        padding: 20px;
        text-align: center;
    }

    /* INPUT FIELDS STYLING */
    .stTextInput input, .stSelectbox div[data-baseweb="select"] > div {
        background-color: rgba(255, 255, 255, 0.9) !important;
        color: #000000 !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 8px !important;
    }

    /* PROFILE CARD STYLING */
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
    
    /* ACTION BUTTONS */
    div.stButton > button {
        background: rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
    }
    
    </style>
    """, unsafe_allow_html=True)

    mode_key = f"profile_mode_{username or 'anon'}"
    switch_flag_key = f"profile_switch_to_view_{username or 'anon'}"

    if st.session_state.get(switch_flag_key):
        st.session_state[mode_key] = "🔒 View"
        st.session_state[switch_flag_key] = False
    h1, h2 = st.columns([6, 2], vertical_alignment="center")
    with h1:
        st.markdown("<h1 style='margin-bottom: 10px;'>👤 My <span style='color:#34d399'>Profile</span></h1>", unsafe_allow_html=True)
    with h2:
        mode = st.radio(
            "",
            ["🔒 View", "✏ Edit"],
            horizontal=True,
            key=mode_key,
        )
    is_edit_mode = mode.startswith("✏")

    c1, c2 = st.columns([1, 2], gap="large")
    with c1:
        inner_avatar_html = "👨‍🌾"
        avatar_b64 = profile.get("avatar_b64")
        if avatar_b64:
            inner_avatar_html = f'<img src="data:image/png;base64,{avatar_b64}" class="avatar-img">'

        st.markdown(f"""
        <div class="profile-card">
            <div style="background: #fbbf24; color: #020617; padding: 6px 16px; border-radius: 50px; font-size: 0.75rem; font-weight: 800; display: inline-block; margin-bottom: 15px;">PRO MEMBER</div>
            <div class="avatar-circle">{inner_avatar_html}</div>
            <h2 style="margin:0; color: white; font-weight: 800;">{real_fullname}</h2>
            <div style="margin-top: 10px;">
                <span style="background: rgba(52,211,153,0.18); color: #d1fae5; padding: 6px 14px; border-radius: 999px; font-size: 0.85rem; font-weight: 700; display: inline-block;">{role_label}</span>
            </div>
            <p style="color: #cbd5e1; margin-top: 25px; font-size: 0.9rem; line-height: 1.6;">
                <b>Joined:</b> {real_join_date}<br>
                <b>Location:</b> {location_value}<br>
                <b>Last Login:</b> {last_login_display}<br>
                <b>Login Device:</b> {last_device_display}
            </p>
        </div>
        """, unsafe_allow_html=True)

        if is_edit_mode:
            uploaded = st.file_uploader(
                "Upload Profile Image",
                type=["png", "jpg", "jpeg"],
                key=f"profile_avatar_uploader_{username or 'anon'}",
            )
            if uploaded and username:
                try:
                    img = Image.open(uploaded)
                    avatar_b64_new = image_to_base64(img)
                    upsert_user_profile(username=username, avatar_b64=avatar_b64_new)
                    st.toast("Profile image updated!", icon="✅")
                    st.rerun()
                except Exception:
                    st.error("Could not process that image. Please upload a valid PNG/JPG.")

        if username:
            total_scans = get_total_scans(username)
        else:
            total_scans = 0
        st.markdown(
            f"""
            <div style="margin-top: 16px; display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
                <div style="background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.10); border-radius: 14px; padding: 12px 14px; text-align: left;">
                    <div style=\"color:#94a3b8; font-size: 0.78rem; font-weight: 700;\">Total Scans</div>
                    <div style=\"color:#ffffff; font-size: 1.15rem; font-weight: 900; margin-top: 4px;\">{total_scans}</div>
                </div>
                <div style="background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.10); border-radius: 14px; padding: 12px 14px; text-align: left;">
                    <div style=\"color:#94a3b8; font-size: 0.78rem; font-weight: 700;\">Member Since</div>
                    <div style=\"color:#ffffff; font-size: 1.15rem; font-weight: 900; margin-top: 4px;\">{real_join_date}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c2:
        with st.container():
            st.markdown("### ⚙️ Account Details")
            if not username:
                st.warning("You must be logged in to edit profile details.")
                return

            default_email = profile.get("email") or f"{username}@agridetect.com"
            default_phone = profile.get("phone") or ""
            default_location = profile.get("location") or ""
            col_form1, col_form2 = st.columns(2)
            with col_form1:
                new_name = st.text_input("Full Name", value=real_fullname, disabled=not is_edit_mode)
                email = st.text_input("Email", value=default_email, disabled=not is_edit_mode)
            with col_form2:
                phone = st.text_input("Phone Number", value=default_phone, disabled=not is_edit_mode)
                role_choice = st.selectbox(
                    "User Role",
                    [role_options[k] for k in ["farmer", "student", "researcher", "consultant"]],
                    index=[role_options[k] for k in ["farmer", "student", "researcher", "consultant"]].index(role_label),
                    disabled=not is_edit_mode,
                )

            location = st.text_input("Location", value=default_location, disabled=not is_edit_mode)
            lang = st.selectbox("App Language", ["English", "Telugu (తెలుగు)", "Hindi (हिंदी)"], disabled=not is_edit_mode)

            st.write("")
            if is_edit_mode:
                if st.button("💾 Save Changes", key=f"save_profile_{username}"):
                    role_key_new = None
                    for k, v in role_options.items():
                        if v == role_choice:
                            role_key_new = k
                            break

                    run_query("UPDATE users SET name = ? WHERE username = ?", (new_name, username))
                    upsert_user_profile(
                        username=username,
                        role=role_key_new,
                        email=email,
                        phone=phone,
                        location=location,
                    )
                    if "user" in st.session_state and st.session_state["user"]:
                        st.session_state["user"]["name"] = new_name
                    st.session_state[switch_flag_key] = True
                    st.toast("Profile updated successfully!", icon="✅")
                    st.rerun()


def profile_page():
    """Standalone profile page used when routing to 'profile'."""
    # Apply the same dashboard background and theme so profile matches
    BANNER_PATH = os.path.join("assets", "banner.png")
    bg_image_base64 = get_base64(BANNER_PATH)
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
    </style>
    """, unsafe_allow_html=True)

    user = st.session_state.get('user')
    c1, c2, c3 = st.columns([1, 9, 2])
    with c1:
        if st.button("⬅ Back", key="profile_back"):
            st.session_state['page'] = 'dashboard'
            st.rerun()
    with c2:
        render_profile_panel(user)
    with c3:
        if st.button("🚪 Logout", key="profile_logout"):
            st.session_state['page'] = 'landing'
            st.session_state['authenticated'] = False
            st.session_state['user'] = None
            st.rerun()

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
            <div class="card"><h3>🧠 Deep Learning Accuracy</h3><p>Built on fine-tuned CNN architectures trained on real agricultural datasets.</p></div>
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
    <div class="custom-footer"> 2026 AgriDetectAI · AI for Smarter Agriculture 🌱</div>
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
        st.markdown('<div class="login-card"><div class="login-title">Welcome Back! </div><p style="color:#d1fae5;">Access your intelligent crop dashboard</p></div>', unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["Login", "Register"])
        
        with tab1:
            with st.form("login_form"):
                username = st.text_input("Username", placeholder="Enter your username")
                password = st.text_input("Password", type="password", placeholder="Enter your password")
                if st.form_submit_button("Log In"):
                    user = authenticate_user(username, password)
                    if user:
                        device = "—"
                        try:
                            ua = getattr(getattr(st, "context", None), "headers", {}).get("User-Agent")
                            if ua:
                                ua_l = str(ua).lower()
                                os_name = "Windows" if "windows" in ua_l else ("Android" if "android" in ua_l else ("iOS" if "iphone" in ua_l or "ipad" in ua_l else "Unknown OS"))
                                browser = "Chrome" if "chrome" in ua_l and "edg" not in ua_l else ("Edge" if "edg" in ua_l else ("Firefox" if "firefox" in ua_l else ("Safari" if "safari" in ua_l and "chrome" not in ua_l else "Browser")))
                                device = f"{os_name} – {browser}"
                        except Exception:
                            device = "—"

                        try:
                            if user.get("username"):
                                update_user_last_login(username=user["username"], device=device)
                        except Exception:
                            pass

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
        if st.button(" Back to Home"):
            st.session_state['page'] = 'landing'
            st.rerun()

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

    h1 {{
        font-weight:900;
        font-size:52px;
        letter-spacing:-1px;
    }}

    /* --- PILL NAVBAR STYLE --- */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 10px;
        background-color: rgba(255, 255, 255, 0.05);
        padding: 10px 20px;
        border-radius: 50px;
        justify-content: center;
        flex-wrap: wrap;
        margin-bottom: 20px;
    }}

    .stTabs [data-baseweb="tab"] {{
        height: 40px;
        border-radius: 40px;
        color: #e2e8f0 !important;
        background-color: transparent;
        border: none;
        font-weight: 600;
        font-size: 0.95rem;
        padding: 0 20px;
    }}

    .stTabs [aria-selected="true"] {{
        background-color: #34d399 !important;
        color: #020617 !important;
        font-weight: 800;
        box-shadow: 0 4px 15px rgba(52, 211, 153, 0.4);
    }}

    [data-testid="stFileUploader"] {{
        width:100% !important;
        padding:2.2rem !important;
        border-radius:20px;
        border:1px dashed rgba(52,211,153,0.7);
        background:rgba(255,255,255,0.05);
    }}

    /* --- DASHBOARD BUTTONS FIX --- */
    div.stButton > button {{
        background: linear-gradient(90deg, #22d3ee, #34d399) !important;
        color: #000000 !important;
        font-weight: 800 !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.6rem 1.2rem !important;
        transition: none !important;
    }}

    /* Ensure button text is black */
    div.stButton > button:hover {{
        transform: scale(1.02) !important;
        box-shadow: 0 0 15px rgba(52, 211, 153, 0.5) !important;
        color: #000000 !important;
    }}

    div.stButton > button p {{
        color: #000000 !important;
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
    col1, col2 = st.columns([8, 2])
    with col2:
        if st.button("🤖 AI Assistant", key="go_chatbot"):
            st.session_state["page"] = "chatbot"
            st.rerun()

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
             


    # --- MAIN ---
    st.markdown("## 🌿 AgriDetectAI Dashboard")
    col1, col2 = st.columns([9, 1])
    with col2:
        if st.button("👤 Profile", help="Open Profile", key="open_profile"):
            st.session_state['page'] = 'profile'
            st.rerun()

    tab_home, tab_analysis, tab_connect, tab_climate, tab_analytics, tab_history, tab_about = st.tabs([
        "🏠 Home",
        "🔬 Analysis",
        "🤝 AgriConnect",
        "🌦️ Climate",
        "📊 Analytics",
        "📜 History",
        "ℹ️ About",
    ])

    # Profile navigation handled by top-level routing (see app.py).

    # =====================================================
    #  TAB
    # =====================================================
    with tab_home:
        # --- 0. SETUP VARIABLES ---
        # Map your existing user dictionary to the variable name used in the new design
        username = user['name']
        from datetime import datetime
        today_date = datetime.now().strftime("%A, %d %B %Y")
 

        # --- 1. CUSTOM CSS FOR THIS TAB ---
        st.markdown("""
        <style>
        /* Section Headers */
        .section-title {
            font-size: 1.8rem;
            font-weight: 800;
            margin-top: 40px;
            margin-bottom: 20px;
            background: linear-gradient(90deg, #34d399, #22d3ee);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        /* Stat Cards (Achievements) */
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

        /* Testimonial Cards */
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

        /* Footer */
        .custom-footer {
            margin-top: 80px;
            padding-top: 40px;
            border-top: 1px solid rgba(255,255,255,0.1);
            text-align: center;
            color: #94a3b8;
        }
        
        /* Footer Links */
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
            <h1 style='font-size: 3rem; margin-bottom: 10px; color: white;'>
                Farm Overview & Daily Insights
            </h1>
            <p style='color: #34d399; font-size: 1.1rem; font-weight: 600; margin-bottom: 15px; letter-spacing: 0.5px;'>
                {today_date} &nbsp; | &nbsp; Nalgonda, Telangana
            </p>
            <p style='color: #cbd5e1; font-size: 1.15rem; line-height: 1.6; max-width: 900px;'>
                Welcome to your command center, <b>{username}</b>. You are currently monitoring 
                <b>12 acres</b> of active cultivation for the <b>Rabi Season</b>. 
            Our AI systems have detected optimal humidity levels for Rice, but please review the 
            <b>3 active alerts</b> regarding Potato Blight in Sector 4.
            Use the tabs above to run new diagnostics or check soil analytics.
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")


        

        # --- 3. LIVE STATUS (The Green/Red Cards) ---
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("""
            <div class="stat-card" style="display: flex; align-items: center; justify-content: space-between;">
                <div style="text-align: left;">
                    <h3 style="margin:0;"> Active Crops</h3>
                    <p style="color: #cbd5e1; margin:0;">Rice (Sona Masoori), Potato</p>
                </div>
                <div style="font-size: 2.5rem;"></div>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown("""
            <div class="stat-card" style="display: flex; align-items: center; justify-content: space-between; border-color: #34d399;">
                <div style="text-align: left;">
                    <h3 style="margin:0; color: #34d399;"> System Status</h3>
                    <p style="color: #cbd5e1; margin:0;">AI Model Online & Ready</p>
                </div>
                <div style="font-size: 2.5rem;"></div>
            </div>
            """, unsafe_allow_html=True)

        # --- 4. COMPANY ACHIEVEMENTS (Grid Layout) ---
        st.markdown('<div class="section-title"> Our Impact</div>', unsafe_allow_html=True)
        
        ac1, ac2, ac3, ac4 = st.columns(4)
        with ac1:
            st.markdown("""
            <div class="stat-card">
                <div class="stat-number">15k+</div>
                <div class="stat-label">Scans Performed</div>
            </div>
            """, unsafe_allow_html=True)
        with ac2:
            st.markdown("""
            <div class="stat-card">
                <div class="stat-number">96%</div>
                <div class="stat-label">Accuracy Rate</div>
            </div>
            """, unsafe_allow_html=True)
        with ac3:
            st.markdown("""
            <div class="stat-card">
                <div class="stat-number">50+</div>
                <div class="stat-label">Villages Covered</div>
            </div>
            """, unsafe_allow_html=True)
        with ac4:
            st.markdown("""
            <div class="stat-card">
                <div class="stat-number">24/7</div>
                <div class="stat-label">Expert Support</div>
            </div>
            """, unsafe_allow_html=True)

        # --- 5. FARMER REVIEWS ---
        st.markdown('<div class="section-title"> What Farmers Say</div>', unsafe_allow_html=True)
        
        rc1, rc2 = st.columns(2)
        
        with rc1:
            st.markdown("""
            <div class="review-card">
                <div class="review-text">"I used to lose 30% of my potato crop to Blight every year. AgriDetect diagnosed it early, and the suggested spray saved my harvest!"</div>
                <div class="review-author"> Ramesh Reddy <span style="font-weight:normal; color:#64748b; font-size:0.9rem;">(Warangal)</span></div>
            </div>
            <div class="review-card">
                <div class="review-text">"The interface is so simple, even my father can use it. The Telugu language support would be great in the future!"</div>
                <div class="review-author"> Sita Lakshmi <span style="font-weight:normal; color:#64748b; font-size:0.9rem;">(Karimnagar)</span></div>
            </div>
            """, unsafe_allow_html=True)
            
        with rc2:
            st.markdown("""
            <div class="review-card">
                <div class="review-text">"Government schemes section is very helpful. I didn't know I was eligible for the PM-Kisan subsidy until I checked here."</div>
                <div class="review-author"> Krishna Rao <span style="font-weight:normal; color:#64748b; font-size:0.9rem;">(Nalgonda)</span></div>
            </div>
            <div class="review-card">
                <div class="review-text">"Best app for Rice Blast detection. The chemical dosage recommendations are very accurate."</div>
                <div class="review-author"> Venkat Goud <span style="font-weight:normal; color:#64748b; font-size:0.9rem;">(Khammam)</span></div>
            </div>
            """, unsafe_allow_html=True)

        # --- 6. FOOTER ---
        st.markdown("""
        <div class="custom-footer">
            <div style="font-size: 1.5rem; font-weight: 800; margin-bottom: 20px;">
                AgriDetect<span style="color: #34d399;">AI</span>
            </div>
            <div class="footer-links">
                <a href="#">About Us</a>
                <a href="#">Privacy Policy</a>
                <a href="#">Terms of Service</a>
                <a href="#">Contact Support</a>
            </div>
            <p style="margin-top: 30px; font-size: 0.8rem; opacity: 0.6;">
                 2026 AgriDetectAI · AI for Smarter Agriculture 
            </p>
        </div>
        """, unsafe_allow_html=True)
        

    # Profile moved: rendering is handled by `render_profile_panel()` when the top-right icon is clicked.

    # =====================================================
    with tab_analysis:
        st.markdown("### AI Disease Diagnosis")

        config_path = os.path.join("config", "model_config.json")

        if not os.path.exists(config_path):
            st.error("Config file not found!")
            return

        with open(config_path) as f:
            config = json.load(f)

        # --- NEW: CROP SELECTION UI ---
        # This allows the user to switch between Rice/Potato and Corn/Blackgram
        # --- CROP SELECTION UI ---
        model_options = {
            "Rice & Potato": "rice_potato",
            "Corn & Blackgram": "corn_blackgram",
            "Cotton & Tomato": "cotton_tomato"
        }

        selected_display_name = st.selectbox(
            " Select Crop Category",
            options=list(model_options.keys())
        )
        
        # This is the internal key used for config and preprocessing logic
        selected_model_name = model_options[selected_display_name]

        st.markdown("---")

        col_left, col_right = st.columns([0.9, 1.1], gap="large")

        with col_left:
            st.markdown("""
            <style>
            [data-testid="stFileUploader"] { color: #000000 !important; }
            [data-testid="stFileUploader"] small, [data-testid="stFileUploader"] span { color: #000000 !important; }
            </style>
            """, unsafe_allow_html=True)

            uploaded_file = st.file_uploader(
                " Upload Leaf Image — JPG / PNG (Max 5MB)",
                type=["jpg", "jpeg", "png"]
            )

            image = None
            if uploaded_file is not None:
                image = Image.open(uploaded_file)
                st.image(image, caption='Your Upload', width=340)

        with col_right:
            if uploaded_file is not None and image is not None:
                st.markdown("#### Diagnosis Report")

                with st.spinner('Scanning leaf tissues...'):

                    model, model_type = load_model(selected_model_name)

                    if not model:
                        st.error("Model failed to load.")
                        return

                    processed_img = preprocess_image(
                        image,
                        model_type=model_type,
                        model_key=selected_model_name
                    )

                    try:
                        predictions = predict_image(model, model_type, processed_img)

                        class_indices = config['models'][selected_model_name]['classes']

                        predicted_class_index = np.argmax(predictions)
                        confidence = np.max(predictions) * 100

                        predicted_label = class_indices.get(
                            str(predicted_class_index),
                            f"Class {predicted_class_index}"
                        )

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

                        chart = alt.Chart(df_chart).mark_bar(
                            cornerRadiusEnd=6
                        ).encode(
                            x=alt.X('Confidence:Q', title=None, axis=alt.Axis(format='%')),
                            y=alt.Y('Condition:N', sort='-x', title=None),
                            color=alt.Color('Confidence:Q', scale=alt.Scale(scheme="blues"), legend=None),
                            tooltip=[
                                alt.Tooltip('Condition:N'),
                                alt.Tooltip('Confidence:Q', format='.2%')
                            ]
                        ).properties(height=350)

                        text = chart.mark_text(
                            align='left',
                            baseline='middle',
                            dx=5
                        ).encode(
                            text=alt.Text('Confidence:Q', format='.1%')
                        )

                        st.altair_chart(chart + text, use_container_width=True)

                        if "analysis_history" not in st.session_state:
                            st.session_state["analysis_history"] = []

                        upload_bytes = uploaded_file.getvalue() if uploaded_file is not None else b""
                        upload_hash = hashlib.sha256(upload_bytes).hexdigest() if upload_bytes else None
                        history_dedupe_key = f"{selected_display_name}||{predicted_label}||{upload_hash}"

                        if history_dedupe_key and st.session_state.get("last_history_key") != history_dedupe_key:
                            st.session_state["analysis_history"].append(
                                {
                                    "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                                    "Image": getattr(uploaded_file, "name", "upload"),
                                    "Crop": selected_display_name,
                                    "Result": predicted_label,
                                    "Confidence": f"{confidence:.2f}%",
                                }
                            )
                            st.session_state["last_history_key"] = history_dedupe_key

                            current_user = st.session_state.get("user")
                            if current_user and current_user.get("username") and upload_hash:
                                try:
                                    add_analysis_history(
                                        username=current_user["username"],
                                        crop_category=selected_display_name,
                                        image_name=getattr(uploaded_file, "name", "upload"),
                                        result=predicted_label,
                                        confidence=float(confidence),
                                        upload_hash=upload_hash,
                                    )
                                except Exception:
                                    pass

                        if "treat_prev_cache" not in st.session_state:
                            st.session_state["treat_prev_cache"] = {}

                        cache_key = f"{selected_display_name}||{predicted_label}"

                        st.markdown("---")
                        st.markdown("#### Treatment & Prevention")

                        if cache_key in st.session_state["treat_prev_cache"]:
                            st.markdown(st.session_state["treat_prev_cache"][cache_key])
                        else:
                            try:
                                with st.spinner("Generating treatment & prevention guidance..."):
                                    advice_md = generate_treatment_prevention(
                                        crop_category=selected_display_name,
                                        disease_label=predicted_label,
                                    )
                                st.session_state["treat_prev_cache"][cache_key] = advice_md
                                st.markdown(advice_md)
                            except Exception as e:
                                st.info("Treatment & prevention suggestions require Gemini API configuration.")
                                st.caption(str(e))

                    except Exception as e:
                        st.error(f"Prediction Error: {e}")

    # --- TAB 2: AGRICONNECT ---
    with tab_connect:
        root_dir = os.getcwd()
        feedback_dir = os.path.join(root_dir, "data")
        feedback_file = os.path.join(feedback_dir, "feedback_log.txt")
        os.makedirs(feedback_dir, exist_ok=True)

        st.markdown("""
        <style>
        h1, h2, h3, h4, h5, p, span, label, div { color: white !important; }

        [data-testid="stForm"] {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 30px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        /* AGRICONNECT BUTTONS FIX (MATCHING LOGIN PAGE) */
        div[data-testid="stFormSubmitButton"] button {
            width: 100% !important;
            background: linear-gradient(90deg, #22d3ee, #34d399) !important;
            color: #000000 !important;
            border-radius: 12px !important;
            font-weight: 800 !important;
            border: none !important;
            padding: 0.8rem !important;
        }

        div[data-testid="stFormSubmitButton"] button:hover {
            transform: scale(1.02) !important;
            box-shadow: 0 0 15px rgba(52, 211, 153, 0.5) !important;
            color: #000000 !important;
        }

        .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] > div {
            background-color: rgba(0, 0, 0, 0.3) !important;
            color: white !important;
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
            border-radius: 12px !important;
        }

        .feedback-card {
            background: rgba(0, 0, 0, 0.2);
            border-left: 4px solid #34d399;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 15px;
        }
        .user-name { color: #34d399 !important; font-weight: bold; }
        .feedback-text { color: #e2e8f0 !important; font-style: italic; }
        </style>
        """, unsafe_allow_html=True)

        st.markdown("<h1 style='text-align: center;'> Community <span style='color:#34d399'>Feedback</span></h1>", unsafe_allow_html=True)
        c1, c2 = st.columns([1.5, 1], gap="large")

        with c1:
            with st.form("user_feedback"):
                st.markdown("### Submit Your Review")
                category = st.radio("Hidden Label", [" Accuracy", " Bug", " Feature", " Other"], horizontal=True, label_visibility="collapsed")
                col_in1, col_in2 = st.columns(2)
                with col_in1: name = st.text_input("Your Name (Optional)")
                with col_in2: crop = st.selectbox("Related Crop", ["General", "Rice", "Potato", "Corn", "Blackgram", "Cotton", "Tomato", "Pumpkin", "Wheat",])
                subject = st.text_input("Subject")
                message = st.text_area("Detailed Feedback", height=120)
                
                c_r1, c_r2 = st.columns(2)
                with c_r1: rating = st.slider("Rate Us", 1, 5, 5)
                with c_r2: accuracy = st.radio("AI Accuracy", ["Yes, Spot on! ", "Partially ", "No, Incorrect "], horizontal=True)

                if st.form_submit_button(" Submit Feedback"):
                    if message:
                        current_user = st.session_state.get("user")
                        username_db = current_user.get("username") if isinstance(current_user, dict) else None
                        display_name_db = name.strip() if name and name.strip() else (current_user.get("name") if isinstance(current_user, dict) else None)
                        try:
                            add_community_feedback(
                                username=username_db,
                                display_name=display_name_db,
                                category=category,
                                crop=crop,
                                subject=subject,
                                message=message,
                                rating=int(rating) if rating is not None else None,
                                accuracy=accuracy,
                            )
                        except Exception:
                            pass
                        st.success(" Thank you!"); st.balloons()
                    else: st.warning("Please enter a message.")
                    # if message:
                    #     with open(feedback_file, "a") as f:
                    #         f.write(f"{name}\n{message}\n\n")
                    #     st.success("Thank you for your feedback!")
                    # else:
                    #     st.warning("Please enter a message.")

        with c2:
            st.markdown("### Recent Activity")
            try:
                recent_rows = get_recent_community_feedback(limit=12)
            except Exception:
                recent_rows = []

            if not recent_rows:
                st.info("No community feedback yet. Be the first to post a review!")
            else:
                cards_html = ""
                for r in recent_rows:
                    created_at, display_name, crop_name, subj, msg, rating_val, accuracy_val = r
                    display = display_name or "Anonymous"
                    subtitle_parts = []
                    if crop_name:
                        subtitle_parts.append(str(crop_name))
                    if subj:
                        subtitle_parts.append(str(subj))
                    if rating_val is not None:
                        subtitle_parts.append(f"Rating: {rating_val}/5")
                    if accuracy_val:
                        subtitle_parts.append(str(accuracy_val).strip())
                    subtitle = " · ".join(subtitle_parts)

                    cards_html += (
                        f'<div class="feedback-card">'
                        f'  <div class="user-name">{display}</div>'
                        f'  <div class="feedback-text">"{str(msg).strip()}"</div>'
                        + (f'  <div style="color:#94a3b8;font-size:0.85rem;margin-top:6px;">{subtitle}</div>' if subtitle else "")
                        + (f'  <div style="color:#64748b;font-size:0.75rem;margin-top:4px;">{created_at}</div>' if created_at else "")
                        + '</div>'
                    )

                st.markdown(cards_html, unsafe_allow_html=True)

    # --- TAB 3: CLIMATE & ALERTS ---
    with tab_climate:
        st.header(" Local Climate & Alerts")
        
        # MOCK METRICS (Looks real but is static for now)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="Temperature", value="28°C", delta="1.2°C")
        with col2:
            st.metric(label="Humidity", value="65%", delta="-5%")
        with col3:
            st.metric(label="Wind Speed", value="12 km/h", delta="Normal")
            
        st.markdown("---")
        
        # ALERTS SECTION
        st.subheader(" Active Disease Alerts")
        
        st.warning("""
        **High Risk Alert: Rice Blast**
        
        **Cause:** High humidity (above 90%) and lower night temperatures detected in your region.
        
        **Action:** Monitor fields closely. Avoid excess nitrogen fertilizer.
        """)
        
        st.info("""
        **Moderate Risk: Potato Late Blight**
        
        **Cause:** Intermittent rains predicted for the next 48 hours.
        """)

    # --- TAB 4: SMART ANALYTICS ---
    with tab_analytics:
        # --- 1. CUSTOM CSS ---
        st.markdown("""
        <style>
        /* KPI CARDS */
        .kpi-card { 
            background: rgba(255, 255, 255, 0.05); 
            backdrop-filter: blur(10px); 
            border-radius: 15px; 
            padding: 20px; 
            border: 1px solid rgba(255, 255, 255, 0.1); 
            text-align: center; 
            transition: transform 0.3s; 
        }
        .kpi-card:hover { 
            transform: translateY(-5px); 
            border-color: #34d399; 
            box-shadow: 0 10px 20px rgba(52, 211, 153, 0.2); 
        }
        .kpi-value { font-size: 2.2rem; font-weight: 800; color: white; margin: 0; }
        .kpi-label { color: #cbd5e1; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1px; }

        /* TABLE STYLES */
        .chart-container { 
            background: rgba(0, 0, 0, 0.2); 
            border-radius: 20px; 
            padding: 20px; 
            border: 1px solid rgba(255, 255, 255, 0.05); 
            margin-bottom: 20px; 
        }
        .report-table { width: 100%; border-collapse: collapse; color: #e2e8f0; font-size: 0.9rem; }
        .report-table th { 
            text-align: left; 
            padding: 15px; 
            border-bottom: 1px solid rgba(255,255,255,0.1); 
            color: #34d399; 
            text-transform: uppercase; 
            font-size: 0.8rem; 
        }
        .report-table td { padding: 15px; border-bottom: 1px solid rgba(255,255,255,0.05); }
        
        /* STATUS BADGES */
        .status-badge { padding: 5px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: bold; }
        .status-high { background: rgba(248, 113, 113, 0.2); color: #f87171; }
        .status-safe { background: rgba(52, 211, 153, 0.2); color: #34d399; }
        </style>
        """, unsafe_allow_html=True)

        # --- 2. HEADER ---
        st.markdown("<h1 style='text-align: center;'> Farm <span style='color:#34d399'>Analytics</span></h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #cbd5e1; margin-bottom: 30px;'>Real-time insights on crop health and yield predictions.</p>", unsafe_allow_html=True)

        # --- 3. KPI SECTION ---
        k1, k2, k3, k4 = st.columns(4)
        with k1: st.markdown('<div class="kpi-card"><div class="kpi-label">Total Scans</div><div class="kpi-value">1,248</div><div style="color: #34d399; font-size: 0.8rem;"> 12% this week</div></div>', unsafe_allow_html=True)
        with k2: st.markdown('<div class="kpi-card"><div class="kpi-label">Avg Health Score</div><div class="kpi-value">87%</div><div style="color: #34d399; font-size: 0.8rem;">Stable</div></div>', unsafe_allow_html=True)
        with k3: st.markdown('<div class="kpi-card"><div class="kpi-label">Disease Alerts</div><div class="kpi-value" style="color: #f87171;">14</div><div style="color: #f87171; font-size: 0.8rem;">Requires Action</div></div>', unsafe_allow_html=True)
        with k4: st.markdown('<div class="kpi-card"><div class="kpi-label">Est. Yield</div><div class="kpi-value">4.2T</div><div style="color: #fbbf24; font-size: 0.8rem;">Potato & Rice</div></div>', unsafe_allow_html=True)

        st.write("") # Spacer

        # --- 4. PREPARE DATA ---
        yield_data = pd.DataFrame({"Crop": ["Rice", "Potato", "Wheat", "Tomato"], "Yield (Tons)": [45, 60, 30, 25]})
        
        # Creating dummy trend data (you'd replace this with real database queries later)
        trend_data = pd.DataFrame({
            "Month": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"], 
            "Healthy": [80, 85, 82, 88, 90, 87], 
            "Diseased": [20, 15, 18, 12, 10, 13]
        })

        # --- 5. CHARTS SECTION ---
        c1, c2 = st.columns(2)
        
        with c1:
            st.markdown("### Crop Yield Forecast")
            # Bar Chart using Plotly Express
            fig_yield = px.bar(yield_data, x="Crop", y="Yield (Tons)", color="Crop", color_discrete_sequence=["#34d399", "#22d3ee", "#fbbf24", "#f87171"])
            
            # Customizing Layout for Dark Theme/Glass Look
            fig_yield.update_layout(
                plot_bgcolor="rgba(0,0,0,0)", 
                paper_bgcolor="rgba(255, 255, 255, 0.05)", 
                font=dict(color="white"), 
                showlegend=False, 
                xaxis=dict(showgrid=False), 
                yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.1)"),
                margin=dict(l=20, r=20, t=20, b=20)
            )
            st.plotly_chart(fig_yield, use_container_width=True)

        with c2:
            st.markdown("### Disease Trends (6 Months)")
            # Area Chart using Graph Objects
            fig_trend = go.Figure()
            fig_trend.add_trace(go.Scatter(x=trend_data["Month"], y=trend_data["Healthy"], fill='tozeroy', mode='lines', name='Healthy', line=dict(width=3, color='#34d399')))
            fig_trend.add_trace(go.Scatter(x=trend_data["Month"], y=trend_data["Diseased"], fill='tozeroy', mode='lines', name='Diseased', line=dict(width=3, color='#f87171')))
            
            # Customizing Layout
            fig_trend.update_layout(
                plot_bgcolor="rgba(0,0,0,0)", 
                paper_bgcolor="rgba(255, 255, 255, 0.05)", 
                font=dict(color="white"), 
                legend=dict(orientation="h", y=1.1), 
                xaxis=dict(showgrid=False), 
                yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.1)"),
                margin=dict(l=20, r=20, t=20, b=20)
            )
            st.plotly_chart(fig_trend, use_container_width=True)

        # --- 6. RECENT REPORTS TABLE ---
        st.markdown("### Recent Field Reports")
        st.markdown("""
        <div class="chart-container">
            <table class="report-table">
                <thead>
                    <tr>
                        <th>Scan ID</th>
                        <th>Date</th>
                        <th>Crop Type</th>
                        <th>Diagnosis</th>
                        <th>Risk Level</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>#SC-2045</td>
                        <td>Feb 24, 2026</td>
                        <td>Potato (Kufri)</td>
                        <td>Early Blight</td>
                        <td><span class="status-badge status-high">High Risk</span></td>
                    </tr>
                    <tr>
                        <td>#SC-2044</td>
                        <td>Feb 23, 2026</td>
                        <td>Rice (Basmati)</td>
                        <td>Healthy</td>
                        <td><span class="status-badge status-safe">Safe</span></td>
                    </tr>
                </tbody>
            </table>
        </div>
        """, unsafe_allow_html=True)

    # --- TAB 5: HISTORY ---
    with tab_history:
        st.header(" Analysis History")
        current_user = st.session_state.get("user")

        history_rows = []
        if current_user and current_user.get("username"):
            try:
                db_rows = get_analysis_history(current_user["username"], limit=200)
                history_rows = [
                    {
                        "Date": r[0],
                        "Image": r[1],
                        "Crop": r[2],
                        "Result": r[3],
                        "Confidence": f"{r[4]:.2f}%" if r[4] is not None else "",
                    }
                    for r in db_rows
                ]
            except Exception:
                history_rows = []

        if not history_rows:
            history_rows = st.session_state.get("analysis_history", [])

        if not history_rows:
            st.info("No analysis history yet. Upload a leaf image in the Analysis tab to generate a record.")
        else:
            st.dataframe(pd.DataFrame(history_rows), use_container_width=True)

    # --- TAB 6: ABOUT ---
    with tab_about:
        st.markdown(
            """
<div style="text-align: center; max-width: 900px; margin: auto; background: transparent; border: none; backdrop-filter: none; -webkit-backdrop-filter: none; padding: 28px 26px; border-radius: 18px; color: #e2e8f0;">

<h2 style="color: #ffffff;">🌿 About AgriDetectAI</h2>

<p>
AgriDetectAI is an intelligent crop health monitoring platform designed to deliver fast, reliable, and field-ready plant disease diagnostics.
Built to empower farmers, researchers, and agricultural institutions, the system leverages advanced artificial intelligence to identify plant leaf diseases with high precision from simple image inputs.
</p>

<p>
By combining deep learning and computer vision, AgriDetectAI transforms traditional crop inspection into a scalable, data-driven solution — enabling early detection, reduced crop loss, and improved agricultural productivity.
</p>

<br>

<h2 style="color: #ffffff;">🧠 Core Capabilities</h2>

<ul style="list-style-type: none; list-style-position: outside; padding-left: 0; margin-left: 0;">
<li>📷 Image-based plant leaf disease detection</li>
<li>🌱 Identification of both healthy and diseased crops</li>
<li>🎯 High-accuracy predictions using specialized AI models</li>
<li>⚡ Fast and responsive analysis suitable for real-world usage</li>
<li>👨‍🌾 User-friendly interface designed for farmers and researchers</li>
<li>📊 Structured and consistent diagnostic outputs</li>
</ul>

<p>
AgriDetectAI focuses on delivering actionable insights rather than just predictions — helping users make informed agricultural decisions.
</p>

<br>

<h2 style="color: #ffffff;">🌾 Crop-Specific AI Architecture</h2>

<p>
AgriDetectAI follows a multi-model architecture where each deep learning model is trained specifically for a defined crop category.
This targeted approach improves classification accuracy and significantly reduces cross-crop misclassification.
</p>

<p><strong>Supported Crop Categories:</strong></p>

<p>
Rice • Potato • Corn • Blackgram • Cotton • Tomato • Pumpkin • Wheat
</p>

<br>

<h2 style="color: #ffffff;">🌍 Why It Matters</h2>

<p>
Plant diseases are one of the leading causes of agricultural yield loss worldwide. Delayed identification often results in large-scale crop damage and financial setbacks for farmers.
</p>

<p>
AgriDetectAI bridges this gap by enabling early-stage detection through accessible, AI-driven technology.
By digitizing plant health monitoring, the platform supports reduced crop loss, faster intervention decisions, data-driven farming practices, and scalable agricultural innovation.
</p>

</div>
            """,
            unsafe_allow_html=True,
        )

def chatbot_page():
    st.markdown('<div class="chatbot-scope">', unsafe_allow_html=True)

    BANNER_PATH = os.path.join("assets", "banner.png")
    bg_image_base64 = get_base64(BANNER_PATH)

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

    header {{ visibility: hidden; }}
    footer {{ visibility: hidden; }}
    </style>
    """, unsafe_allow_html=True)
    st.markdown("""
<style>

/* =========================
   CHATBOT VISIBILITY FIX
   (Same dark background)
   ========================= */

/* Chat container */
.ad-chat-box {
    background: rgba(255,255,255,0.06) !important;
    border-radius: 14px;
    box-shadow: 0 15px 15px rgba(0,0,0,0.35);
}

/* Chat header */
.ad-chat-header h2 {
    color: #ffffff !important;
}
.ad-chat-header p {
    color: #cbd5e1 !important;
}

/* Chat messages */
.stChatMessage p {
    color: #ffffff !important;
}

/* Assistant bubble */
[data-testid="stChatMessage"] div:has(svg) {
    background: rgba(255,255,255,0.08) !important;
    border-radius: 10px;
    padding: 5px;
}

/* User bubble */
[data-testid="stChatMessage"] div:not(:has(svg)) {
    background: rgba(34,211,153,0.18) !important;
    border-radius: 10px;
    padding: 5px;
}

/* Suggested question buttons */
button[kind="secondary"] {
    background: rgba(255,255,255,0.12) !important;
    color: #ffffff !important;
    border: 1px solid rgba(255,255,255,0.25) !important;
    border-radius: 12px !important;
    box-shadow: none !important;
}

/* Disable hover-only visibility */
button[kind="secondary"]:hover {
    background: rgba(255,255,255,0.18) !important;
    color: #ffffff !important;
}

/* Reset + Back buttons */
div.stButton > button {
    background: linear-gradient(90deg, #22d3ee, #34d399) !important;
    color: #000000 !important;
    font-weight: 700 !important;
    border-radius: 10px !important;
}

/* No hover color switch */
div.stButton > button:hover {
    background: linear-gradient(90deg, #22d3ee, #34d399) !important;
    color: #000000 !important;
}

/* Chat input */
textarea, input {
    background: rgba(255,255,255,0.12) !important;
    color: #080808 !important;
    border: 1px solid rgba(255,255,255,0.25) !important;
    border-radius: 12px !important;
}

/* Footer text */
.ad-chat-footer {
    color: #94a3b8 !important;
}

</style>
""", unsafe_allow_html=True)



    if st.button("⬅ Back to Dashboard", key="back_dashboard"):
        st.session_state["page"] = "dashboard"
        st.rerun()
    load_dotenv()

# ================== CONFIG ==================
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    if GEMINI_API_KEY:
        genai.configure(api_key=GEMINI_API_KEY)

    # Auto-detect available model
    GEMINI_MODEL = None
    try:
        for model in genai.list_models():
            if "generateContent" in model.supported_generation_methods:
                GEMINI_MODEL = model.name
                break
    except Exception:
        # Fallback if list fails
        GEMINI_MODEL = "models/gemini-pro"

    SYSTEM_PROMPT = """
    You are AgriDetect AI, a friendly agricultural assistant. You help farmers with:
    - Crop disease identification, symptoms, and treatment
    - Prevention strategies and cultural practices
    - Pesticide and fungicide guidance (safety, dosage, timing)
    - Seasonal farming tips and best practices
    - General agriculture questions
    Be concise but helpful. Use bullet points and formatting when useful.
    If unsure, recommend consulting a local agricultural expert.
    """

    FALLBACK_QUESTIONS = [
        "What are the best organic treatments for tomato blight?",
        "How can I prevent powdery mildew in my wheat crop?",
        "When is the best time to apply fungicides?",
        "What crops are resistant to bacterial wilt?",
    ]

    # ================== SESSION STATE ==================
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": (
                    "Hello! I'm your **AgriDetect AI assistant 🌱**\n\n"
                    "• **Disease identification & treatment**\n"
                    "• **Prevention strategies**\n"
                    "• **Seasonal farming tips**\n"
                    "• **Pesticide guidance & safety**\n\n"
                    "_If you see a rate-limit message, wait a minute and try again._"
                ),
                "time": datetime.now(),
            }
        ]

    if "suggested_questions" not in st.session_state:
        st.session_state.suggested_questions = FALLBACK_QUESTIONS

    if "typing" not in st.session_state:
        st.session_state.typing = False


    # ================== FUNCTIONS ==================
    def fetch_suggestions():
        try:
            gemini_key = os.getenv("GEMINI_API_KEY")
            if not gemini_key or not GEMINI_MODEL:
                return
            
            model = genai.GenerativeModel(GEMINI_MODEL)
            instruction = (
                SYSTEM_PROMPT
                + "\n\nSuggest exactly 4 short questions a farmer might ask. Return ONLY a JSON array of strings, nothing else."
            )
            
            try:
                response = model.generate_content(instruction)
                text = response.text.strip()
            except Exception as e:
                # Don't retry on first load to avoid blocking
                if "429" in str(e) or "quota" in str(e).lower():
                    return  # Skip on rate limit
                raise
            
            # Try to parse JSON from the response
            try:
                # Extract JSON if wrapped in markdown or extra text
                if "```json" in text:
                    text = text.split("```json")[1].split("```")[0].strip()
                elif "[" in text:
                    text = text[text.index("["):text.rindex("]")+1]
                
                st.session_state.suggested_questions = json.loads(text)
            except Exception:
                # Fallback if JSON parsing fails
                pass
        except Exception:
            pass
    


    def get_ai_response(user_input):
        st.session_state.typing = True

        gemini_key = os.getenv("GEMINI_API_KEY")
        reply = None

        if not gemini_key or not GEMINI_MODEL:
            reply = "❌ Gemini API not configured or no model available."
        else:
            try:
                model = genai.GenerativeModel(GEMINI_MODEL, system_instruction=SYSTEM_PROMPT)
                
                # Build message history for the model (only include completed messages, not typing state)
                messages = []
                for msg in st.session_state.messages:
                    msg_role = msg.get("role", "user")
                    msg_content = msg.get("content", "")
                    if msg_role == "assistant" and msg_content:
                        messages.append({
                            "role": "model",
                            "parts": msg_content
                        })
                    elif msg_role == "user" and msg_content:
                        messages.append({
                            "role": "user",
                            "parts": msg_content
                        })
                
                # Add current user input
                messages.append({"role": "user", "parts": user_input})
                
                # Retry logic for rate limiting
                max_retries = 3
                retry_delay = 5
                
                for attempt in range(max_retries):
                    try:
                        response = model.generate_content(messages)
                        reply = response.text if response and response.text else "⚠️ Gemini returned empty response."
                        break  # Success, exit retry loop
                    except Exception as e:
                        error_msg = str(e)
                        # Check if it's a rate limit error (429)
                        if "429" in error_msg or "quota" in error_msg.lower():
                            if attempt < max_retries - 1:
                                st.session_state.typing = False
                                with st.spinner(f"⏳ Rate limited. Retrying in {retry_delay} seconds..."):
                                    time.sleep(retry_delay)
                                st.session_state.typing = True
                                retry_delay *= 2  # Exponential backoff
                            else:
                                reply = (
                                    "⏱️ **Rate Limit Exceeded**\n\n"
                                    "Free tier is limited to 5 requests/minute. "
                                    "Please wait a moment and try again, or upgrade your API plan at https://ai.google.dev/"
                                )
                        else:
                            # Other error
                            reply = f"❌ Gemini Error: {error_msg}"
                            break
                
                if not reply:
                    reply = "⚠️ No response received. Please try again."
                    
            except Exception as e:
                reply = f"❌ Unexpected Error: {str(e)}"

        # Ensure we always add a response message
        if reply:
            st.session_state.messages.append({"role": "assistant", "content": reply, "time": datetime.now()})
        
        st.session_state.typing = False
    

    def show():
        # ================== CONFIG CHECK ==================
        gemini_key = os.getenv("GEMINI_API_KEY")
        
        if not gemini_key:
            st.error(
                "⚠️ **Gemini API Key Required**\n\n"
                "Please configure your Gemini API key:\n\n"
                "1. Create a `.env` file in the project root\n"
                "2. Add: `GEMINI_API_KEY=your_api_key_here`\n"
                "3. Restart the app\n\n"
                "Get your API key from: https://ai.google.dev/"
            )
            st.stop()
        
        if not GEMINI_MODEL:
            st.error(
                "⚠️ **No Compatible Gemini Models Available**\n\n"
                "Your API key doesn't have access to any Gemini models.\n\n"
                "1. Check your API key is valid at https://ai.google.dev/\n"
                "2. Ensure the Generative Language API is enabled\n"
                "3. Try creating a new API key with proper permissions\n"
                "4. Restart the app after updating your key"
            )
            st.stop()
        
        # ================== UI (Centered) ==================
        # Compact styling and centered column similar to chat interfaces
        st.markdown(
            """
            <style>
            .ad-chat-box { max-width: 900px; margin: 0 auto; padding: 18px; border-radius: 12px; background: rgba(255,255,255,0.02); }
            .ad-chat-header { text-align: center; margin-bottom: 8px; }
            .ad-suggest-title { margin-top: 12px; font-weight: 700; }
            </style>
            """,
            unsafe_allow_html=True,
        )

        # Create three columns and render the chat in the middle one
        left_col, mid_col, right_col = st.columns([1, 2, 1])
        with mid_col:
            st.markdown('<div class="ad-chat-box">', unsafe_allow_html=True)
            
            
            # Header
            st.markdown(
                "<div class=\"ad-chat-header\">\n<h2>🌱 Chat with AgriDetect AI</h2>\n<p style=\"color:gray; margin-top:-10px;\">Get instant help on crop diseases, treatments, and farming practices</p>\n</div>",
                unsafe_allow_html=True,
            )

            # Initialize session keys if missing (ensure safe on repeated calls)
            if "messages" not in st.session_state:
                st.session_state.messages = [
                    {
                        "role": "assistant",
                        "content": (
                            "Hello! I'm your **AgriDetect AI assistant 🌱**\n\n"
                            "• **Disease identification & treatment**\n"
                            "• **Prevention strategies**\n"
                            "• **Seasonal farming tips**\n"
                            "• **Pesticide guidance & safety**\n\n"
                            "_If you see a rate-limit message, wait a minute and try again._"
                        ),
                        "time": datetime.now(),
                    }
                ]

            if "suggested_questions" not in st.session_state:
                st.session_state.suggested_questions = FALLBACK_QUESTIONS

            if "typing" not in st.session_state:
                st.session_state.typing = False

            # Fetch suggestions once
            if len(st.session_state.messages) == 1:
                fetch_suggestions()

            # Chat messages
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

            if st.session_state.typing:
                with st.chat_message("assistant"):
                    st.markdown("⏳ *AgriDetect AI is typing...*")

            # Suggested questions
            if len(st.session_state.messages) <= 2:
                st.markdown("<div class=\"ad-suggest-title\">💡 Suggested Questions</div>", unsafe_allow_html=True)
                cols = st.columns(2)
                for i, q in enumerate(st.session_state.suggested_questions):
                    with cols[i % 2]:
                        button_key = f"chatbot_q_{i}_btn"
                        if st.button(q, key=button_key, use_container_width=True):
                            st.session_state.messages.append(
                                {"role": "user", "content": q, "time": datetime.now()}
                            )
                            get_ai_response(q)
                            st.rerun()

            # Input
            prompt = st.chat_input("Ask about crop diseases, prevention, treatments...")

            if prompt:
                st.session_state.messages.append(
                    {"role": "user", "content": prompt, "time": datetime.now()}
                )
                get_ai_response(prompt)
                st.rerun()

            # Footer
            st.markdown(
                "<p style='text-align:center;font-size:12px;color:gray;'>"
                "AgriDetect AI provides guidance. Always consult local agricultural experts for critical decisions."
                "</p>",
                unsafe_allow_html=True,
            )

            # Reset
            if st.button("🔄 Reset Chat", key="chatbot_reset_btn"):
                for k in ("messages", "suggested_questions", "typing"):
                    if k in st.session_state:
                        del st.session_state[k]
                st.rerun()

            st.markdown('</div>', unsafe_allow_html=True)

    show()
    
                        

    
    