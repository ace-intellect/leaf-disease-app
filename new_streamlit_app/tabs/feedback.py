import streamlit as st
import os
from datetime import datetime
import time

# --- PATH SETUP ---
current_dir = os.path.dirname(os.path.abspath(__file__)) 
parent_dir = os.path.dirname(current_dir)
root_dir = os.path.dirname(parent_dir)
feedback_file = os.path.join(root_dir, "data", "feedback_log.txt")

# Ensure 'data' folder exists
os.makedirs(os.path.join(root_dir, "data"), exist_ok=True)

def show():
    # --- CSS: SCOPED TO THIS PAGE ---
    st.markdown("""
    <style>
    /* 1. FORCE WHITE TEXT GLOBALLY */
    h1, h2, h3, h4, h5, p, span, label, div { color: white !important; }

    /* 2. FORM CONTAINER */
    [data-testid="stForm"] {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 30px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* 3. INPUTS (White BG, Black Text) */
    .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] > div {
        background-color: rgba(255, 255, 255, 0.9) !important;
        color: black !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 8px !important;
    }
    
    /* 4. BUTTONS (Grey) */
    .stButton button {
        background: rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
    }

    /* 5. FEEDBACK RADIO BUTTONS (SCOPED TO FORM ONLY!) */
    /* This selector ensures we DO NOT touch the Navbar, which is outside the form */
    
    /* Reset Container */
    [data-testid="stForm"] div[data-testid="stRadio"] > div {
        background-color: transparent !important;
        border: none !important;
        padding: 0 !important;
        gap: 10px !important;
    }
    
    /* Unselected Item */
    [data-testid="stForm"] div[data-testid="stRadio"] label {
        background-color: transparent !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 8px !important; 
        padding: 8px 16px !important;
        margin: 0 !important;
    }
    
    /* Selected Item (Green Border, Transparent BG) */
    [data-testid="stForm"] div[data-testid="stRadio"] label[data-baseweb="radio"] {
        background-color: rgba(52, 211, 153, 0.1) !important; 
        border: 1px solid #34d399 !important;
        color: #34d399 !important;
    }
    
    /* Text Color Inside Selected */
    [data-testid="stForm"] div[data-testid="stRadio"] label[data-baseweb="radio"] p {
        color: #34d399 !important;
    }

    /* 6. FEEDBACK CARD (Right Side) */
    .feedback-card {
        background: rgba(0, 0, 0, 0.2);
        border-left: 4px solid #34d399;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
        transition: transform 0.2s;
    }
    .feedback-card:hover { transform: translateX(5px); background: rgba(0, 0, 0, 0.3); }
    .user-name { color: #34d399 !important; font-weight: bold; font-size: 0.9rem; margin-bottom: 5px; }
    .feedback-text { color: #e2e8f0 !important; font-size: 0.95rem; font-style: italic; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<h1 style='text-align: center;'>💬 Community <span style='color:#34d399'>Feedback</span></h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #cbd5e1; margin-bottom: 40px;'>Help us improve the AI by sharing your field experience.</p>", unsafe_allow_html=True)

    c1, c2 = st.columns([1.5, 1], gap="large")

    with c1:
        # The CSS above specifically targets elements inside this form ID
        with st.form("user_feedback"):
            st.markdown("### 📝 Submit Your Review")
            st.markdown("<p style='margin-bottom: 5px; color:#cbd5e1 !important;'>What is this feedback about?</p>", unsafe_allow_html=True)
            category = st.radio("Hidden Label", ["🌱 Accuracy", "🐛 Bug", "💡 Feature", "❤️ Other"], horizontal=True, label_visibility="collapsed")

            st.write("")
            col_in1, col_in2 = st.columns(2)
            with col_in1: name = st.text_input("Your Name (Optional)", placeholder="e.g. Rahul Verma")
            with col_in2: crop = st.selectbox("Related Crop", ["General", "Rice", "Potato", "Wheat", "Tomato", "Cotton"])

            subject = st.text_input("Subject", placeholder="Brief summary...")
            message = st.text_area("Detailed Feedback", placeholder="Describe your experience or issue...", height=120)

            st.write(""); st.markdown("---")
            c_r1, c_r2 = st.columns(2)
            with c_r1:
                st.markdown("**Overall Experience**")
                rating = st.slider("Rate Us", 1, 5, 5, label_visibility="collapsed")
            with c_r2:
                st.markdown("**Did the AI diagnose correctly?**")
                accuracy = st.radio("AI Accuracy", ["Yes, Spot on! ✅", "Partially ⚠️", "No, Incorrect ❌"], horizontal=True, label_visibility="collapsed")

            st.write("")
            # This button will use the Grey style defined in the CSS above
            submitted = st.form_submit_button("🚀 Submit Feedback")
            
            if submitted:
                if message:
                    try:
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        entry = f"[{timestamp}] | Rating: {rating}/5 | Topic: {category} | Name: {name} | Crop: {crop} | Message: {message}\n"
                        with open(feedback_file, "a") as f: f.write(entry)
                        with st.spinner("Sending..."): time.sleep(1.0)
                        st.success("✅ Thank you!"); st.balloons()
                    except Exception as e: st.error(f"Error: {e}")
                else: st.warning("Please enter a message.")

    with c2:
        st.markdown("### 🌍 Recent Activity")
        st.markdown("""
        <div class="feedback-card"><div class="user-name">Venkatesh K.</div><div class="star-rating">⭐⭐⭐⭐⭐</div><div class="feedback-text">"Rice Blast detection saved my crop!"</div></div>
        <div class="feedback-card" style="border-left-color: #fbbf24;"><div class="user-name">Sarah Jenkins</div><div class="star-rating">⭐⭐⭐⭐</div><div class="feedback-text">"Great accuracy on Potato Late Blight."</div></div>
        """, unsafe_allow_html=True)