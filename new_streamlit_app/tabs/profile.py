import streamlit as st
import base64
from PIL import Image
from io import BytesIO

def image_to_base64(image):
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

def show(username):
    user_data = st.session_state.get('user', {})
    real_fullname = user_data.get('name', 'Farmer')
    real_join_date = user_data.get('created_at', '2026-01-01')[:10] 
    
    st.markdown("""
    <style>
    /* 1. RESTORED: GRADIENT UPLOAD BUTTON (Matches Doctor) */
    [data-testid="stFileUploader"] button {
        background: linear-gradient(90deg, #22d3ee, #34d399) !important;
        color: #020617 !important; /* Black Text */
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

    /* 2. BLACK TEXT IN INPUTS */
    .stTextInput input, .stSelectbox div[data-baseweb="select"] > div {
        background-color: rgba(255, 255, 255, 0.9) !important;
        color: black !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 8px !important;
    }
    
    /* 3. PROFILE CARD */
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
    
    /* 4. ACTION BUTTONS (Grey Glass) */
    div.stButton > button {
        background: rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
    }
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
            <p style="color: #cbd5e1; margin-top: 25px; font-size: 0.9rem; line-height: 1.6;">
                <b>Joined:</b> {real_join_date}<br>
                <b>Location:</b> Nalgonda, TG
            </p>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        with st.container():
            st.markdown("### ⚙️ Account Details")
            col_form1, col_form2 = st.columns(2)
            with col_form1:
                new_name = st.text_input("Full Name", value=real_fullname)
                email = st.text_input("Email", value=f"{username}@agridetect.com", disabled=True)
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
                    st.session_state['user']['name'] = new_name
                    st.toast("Profile updated!", icon="✅")
                    st.rerun()
            with b2: st.button("🔑 Change Pass")