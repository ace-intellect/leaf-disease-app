import streamlit as st
import os
import base64

# --- HELPER: BASE64 IMAGE LOADER ---
def get_base64(file_path):
    """Converts an image file to a base64 string for HTML embedding."""
    # We look for assets in the ROOT directory
    # If running from root, 'assets/banner.png' is correct.
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

def show():
    # --- SETUP ASSETS ---
    # Ensure these files exist in your 'assets' folder!
    BANNER_PATH = os.path.join("assets", "banner.png")
    bg_image_base64 = get_base64(BANNER_PATH)

    flow_images = {
        "login": os.path.join("assets", "login.png"),
        "upload": os.path.join("assets", "upload.png"),
        "ai": os.path.join("assets", "ai.png"),
        "disease": os.path.join("assets", "disease.png"),
        "insights": os.path.join("assets", "insights.png")
    }
    # Convert all flow images to base64
    flow_base64 = {k: get_base64(v) for k, v in flow_images.items()}

    # --- YOUR ORIGINAL CSS (Preserved) ---
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap');
    html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; }}

    /* BACKGROUND IMAGE OVERRIDE */
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

    /* FLOW DIAGRAM ITEMS */
    .flow-container {{ display: flex; flex-wrap: wrap; justify-content: center; gap: 20px; }}
    .flow-item {{ flex: 1; min-width: 150px; text-align: center; padding: 24px; background: rgba(255,255,255,0.05); border-radius: 20px; border: 1px solid rgba(255,255,255,0.05); transition: all 0.3s ease; }}
    .flow-item:hover {{ background: rgba(255,255,255,0.1); transform: translateY(-5px); border-color: #22d3ee; }}
    .flow-img {{ width: 64px; height: 64px; margin-bottom: 15px; border-radius: 12px; object-fit: cover; }}
    .flow-title {{ font-weight: 700; color: #ecfeff; }}

    .custom-footer {{ text-align: center; padding: 50px; color: #5eead4; opacity: 0.7; font-size: 0.9rem; }}
    @keyframes fadeUp {{ from {{ opacity: 0; transform: translateY(40px); }} to {{ opacity: 1; transform: translateY(0); }} }}
    </style>
    """, unsafe_allow_html=True)

    # --- LANDING PAGE HTML ---
    st.markdown("""
    <div class="hero">
        <h1>AgriDetect<span>AI</span></h1>
        <p>An intelligent crop-health platform that detects plant diseases early, explains risks clearly, and helps farmers protect yield using AI.</p>
    </div>
    """, unsafe_allow_html=True)

    # --- MAIN ACTION BUTTON ---
    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        # This button switches the state to 'login'
        if st.button("Get Started / Login ➔", use_container_width=True):
            st.session_state['page'] = 'login'
            st.rerun()

    # --- FEATURES SECTION ---
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

    # --- HOW IT WORKS (FLOW) SECTION ---
    # Only render if images were found, otherwise show text fallback
    if flow_base64.get('login'):
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
    else:
        # Fallback if images are missing in assets folder
        st.markdown("""
        <div class="section">
            <h2>How It Works</h2>
            <div class="grid">
                <div class="card"><h3>1. Login</h3></div>
                <div class="card"><h3>2. Upload</h3></div>
                <div class="card"><h3>3. AI Scan</h3></div>
                <div class="card"><h3>4. Result</h3></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # --- FOOTER ---
    st.markdown("""
    <div class="custom-footer">© 2026 AgriDetectAI · AI for Smarter Agriculture 🌱</div>
    """, unsafe_allow_html=True)