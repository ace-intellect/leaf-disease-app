import streamlit as st
import time
import pandas as pd
import numpy as np
from PIL import Image
import json
import os
import base64
import altair as alt
from pathlib import Path


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

    h1{{
        font-weight:900;
        font-size:52px;
        letter-spacing:-1px;
    }}

    .stTabs [data-baseweb="tab-list"]{{
        gap:40px;
        justify-content:center;
    }}

    .stTabs [data-baseweb="tab"]{{
        color:#ffffff !important;
        font-weight:600;
        font-size:18px;
    }}

    .stTabs [aria-selected="true"]{{
        color:#00FFC6 !important;
        border-bottom:3px solid #00FFC6 !important;
    }}

    [data-testid="stFileUploader"] {{
        width:100% !important;
        padding:2.2rem !important;
        border-radius:20px;
        border:1px dashed rgba(52,211,153,0.7);
        background:rgba(255,255,255,0.05);
    }}

    section[data-testid="stFileUploaderDropzone"] {{
        padding:3rem !important;
    }}

    [data-testid="stFileUploader"] small {{
        white-space:normal !important;
        display:block !important;
        color:#d1fae5 !important;
    }}

    [data-testid="stFileUploader"] button{{
        background:linear-gradient(135deg,#00FFC6,#00E0FF) !important;
        color:black !important;
        font-weight:800 !important;
        border-radius:14px !important;
        border:none !important;
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

    # --- MAIN ---
    st.title("🌿 AgriDetectAI Dashboard")
    # --- LOGOUT BUTTON (Styled like Login Button) ---
    # --- SMALL LOGOUT BUTTON TOP-RIGHT ---
    col1, col2 = st.columns([9, 1])  # Push button to right
    with col2:
        if st.button("🚪", help="Logout"):
            st.session_state['authenticated'] = False
            st.session_state['user'] = None
            st.session_state['page'] = 'landing'
            st.rerun()


    tab_home, tab_profile, tab_analysis, tab_connect, tab_climate, tab_analytics, tab_history, tab_about = st.tabs([
        "🏠 Home", "👤 Profile", "🔍 Analysis", "🤝 AgriConnect", "🌦️ Climate", "📊 Analytics", "📜 History", "ℹ️ About"
    ])

    # =====================================================
    # 🏠 HOME TAB
    # =====================================================
    with tab_home:
        st.header("🏠 Welcome to AgriDetectAI")
        st.markdown(f"""
        Hello **{user['name']}**, welcome back to your farm intelligence dashboard! 🌿

        Here you can:
        - Upload leaf images to detect diseases instantly.
        - Monitor your local climate and receive early disease alerts.
        - Track historical analysis and yield projections.
        - Connect with the AgriConnect community for advice and discussions.

        💡 **Tip:** Keep your crop images clear and well-lit for the most accurate AI predictions.
        """)
        

    # =====================================================
    # 👤 PROFILE TAB
    # =====================================================
    with tab_profile:
        st.header("👤 User Profile")
        
        st.subheader("Personal Information")
        st.markdown(f"""
        **Name:** {user['name']}  
        **Email:** {user.get('email', 'Not Provided')}  
        **Joined On:** {user.get('join_date', 'N/A').split(' ')[0]}  
        """)
        
        st.subheader("Farm Details")
        st.markdown("""
        - Farm Size: 5 hectares  
        - Main Crops: Rice, Potato, Tomato  
        - Location: Not Provided  
        """)
        
        st.subheader("Account Settings")
        st.markdown("""
        You can update your account preferences, change your password, or connect with other farmers through AgriConnect.  
        """)
        
        if st.button("Update Profile"):
            st.success("Profile update page coming soon!")

    # =====================================================
    # 🔍 ANALYSIS TAB
    # =====================================================
    with tab_analysis:
     st.markdown("### AI Disease Diagnosis")

    # ---------- LOAD CONFIG ----------
    config_path = os.path.join("config", "model_config.json")

    if not os.path.exists(config_path):
        st.error("Config file not found!")
        return

    with open(config_path) as f:
        config = json.load(f)

    # ---------- MODEL SELECTION UI (LIKE YOUR IMAGE) ----------
    model_options = {
        "Rice & Potato": "rice_potato",
        "Corn & Blackgram": "corn_blackgram",
        "Cotton & Tomato": "cotton_tomato",
    }

    col_select, _ = st.columns([2, 2])

    with col_select:
        selected_display_name = st.selectbox(
            "🎯 Select Crop Category",
            options=list(model_options.keys())
        )

    selected_model_name = model_options[selected_display_name]

    st.markdown("---")

    # ---------- IMAGE UPLOAD ----------
    left, center, right = st.columns([1, 6, 1])

    with center:
        st.info("📸 Upload a clear leaf image")

        uploaded_file = st.file_uploader(
            "🌿 Upload Leaf Image — JPG / PNG (Max 5MB)",
            type=["jpg", "jpeg", "png"]
        )

    if uploaded_file is None:
        return

    image = Image.open(uploaded_file).convert("RGB")

    col1, col2 = st.columns([1, 1.5])

    with col1:
        st.image(image, caption="Your Upload", use_container_width=True)

    # ---------- PREDICTION ----------
    with col2:
        st.markdown("#### 🔬 Diagnosis Report")

        with st.spinner("Scanning leaf tissues..."):
            model, model_type = load_model(selected_model_name)

            if not model:
                st.error("Model failed to load.")
                return

            processed_img = preprocess_image(image, model_type)
            predictions = predict_image(model, model_type, processed_img)

            class_indices = config["models"][selected_model_name]["classes"]

            predicted_class_index = int(np.argmax(predictions))
            confidence = float(np.max(predictions)) * 100

            predicted_label = class_indices.get(
                str(predicted_class_index),
                f"Class {predicted_class_index}"
            )

            # ---------- RESULT ----------
            if "healthy" in predicted_label.lower():
                st.success(f"✅ **{predicted_label}**")
                st.balloons()
            else:
                st.error(f"🦠 **{predicted_label}**")

            st.caption(f"Confidence: {confidence:.2f}%")
            st.progress(int(confidence))

            # ---------- PROBABILITY CHART ----------
            probs = predictions[0]

            df_chart = pd.DataFrame({
                "Condition": [
                    class_indices.get(str(i), f"Class {i}")
                    for i in range(len(probs))
                ],
                "Confidence": probs
            }).sort_values(by="Confidence", ascending=False)

            chart = alt.Chart(df_chart).mark_bar(
                cornerRadiusEnd=6
            ).encode(
                x=alt.X("Confidence:Q", title=None, axis=alt.Axis(format="%")),
                y=alt.Y("Condition:N", sort="-x", title=None),
                color=alt.Color("Confidence:Q", scale=alt.Scale(scheme="blues"), legend=None),
                tooltip=[
                    alt.Tooltip("Condition:N"),
                    alt.Tooltip("Confidence:Q", format=".2%")
                ]
            ).properties(height=350)

            st.altair_chart(chart, use_container_width=True)


    # --- TAB 2: AGRICONNECT ---
    with tab_connect:
        st.header("🤝 AgriConnect Community")
        st.markdown("Connect with researchers and neighboring farmers.")
        
        # Mock Feed
        st.subheader("📢 Recent Discussions")
        
        with st.container():
            st.info("**Topic: New Rice Blast Treatment**\n\n*Dr. A. Sharma:* We are seeing good results with Tricyclazole 75% WP. Has anyone else tried it?")
            st.caption("2 hours ago • 15 replies")
            
        with st.container():
            st.success("**Topic: Potato Yields this Season**\n\n*Farmer John:* My harvest is up 20% thanks to early detection! Checking the soil pH really helped.")
            st.caption("5 hours ago • 8 replies")
            
        st.markdown("---")
        st.text_input("Ask a question or share an update...", placeholder="Type here...")
        st.button("Post to Community")

    # --- TAB 3: CLIMATE & ALERTS ---
    with tab_climate:
        st.header("🌦️ Local Climate & Alerts")
        
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
        st.subheader("⚠️ Active Disease Alerts")
        
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
        st.header("📊 Smart Farm Analytics")
        st.markdown("Visualizing your farm's health and yield potential.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Yield Prediction (tons/ha)")
            # Generate pretty area chart
            chart_data = pd.DataFrame(
                np.random.rand(20, 1) * 10 + 50, # Random values between 50-60
                columns=['Projected Yield']
            )
            st.area_chart(chart_data, color="#4CAF50")
            
        with col2:
            st.subheader("Disease Occurrence Rate")
            # Bar chart
            disease_data = pd.DataFrame({
                'Disease': ['Rice Blast', 'Brown Spot', 'Healthy', 'Sheath Blight'],
                'Occurrences': [12, 5, 45, 8]
            })
            st.bar_chart(disease_data.set_index('Disease'))
            
        st.markdown("---")
        st.subheader("💡 Insights")
        st.success("Your crop health index is **82%**, which is **12% higher** than the regional average.")

    # --- TAB 5: HISTORY ---
    with tab_history:
        st.header("📜 Analysis History")
        st.dataframe(pd.DataFrame({
            "Date": ["2023-10-01", "2023-10-05", "2023-10-12"],
            "Image": ["IMG_2022.jpg", "IMG_2025.jpg", "IMG_2030.jpg"],
            "Result": ["Healthy", "Rice Blast", "Healthy"],
            "Confidence": ["99%", "87%", "95%"]
        }))

    # --- TAB 6: ABOUT ---
    with tab_about:
        st.header("ℹ️ About Agri-AI")
        st.markdown("""
        **Agri-AI** is a cutting-edge leaf disease detection platform designed to empower farmers with instant, laboratory-grade diagnostics. It is an AI-powered web application designed to detect plant leaf diseases and healthy conditions across multiple crops using deep learning and computer vision. The system integrates four specialized models, each trained to handle specific crop groups, ensuring higher accuracy and scalability.
        
        ### 🧠 The Engine
        * **📸 Image-based leaf disease detection
        * **🤖 Deep Learning models trained on crop-specific datasets
        * **🌾 Support for multiple crops through modular model integration
        * **🌐 User-friendly web interface for farmers and researchers           
        
        ### 🌿 AI Models Designed for Crop-Specific Precision
        AgriDetectAI leverages a **multi-model architecture** where each neural network specializes in a defined crop category. This targeted approach enhances prediction accuracy and minimizes cross-crop misclassification.
        **Model Coverage:**
                    - **Rice & Potato**
                    - **Corn & Blackgram**
                    - **Cotton & Tomato**
                    - **Pumpkin & Wheat**
        Across all models, the system identifies both **diseased and healthy leaves**, enabling fast, dependable plant health assessments and supporting data-driven agricultural practices.
        """)

                        

    
    