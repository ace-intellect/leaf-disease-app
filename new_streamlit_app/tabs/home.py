import streamlit as st

# --- UPDATE: Accept 'username' as an argument ---
def show(username):
    # --- CUSTOM CSS FOR THIS PAGE ---
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
    </style>
    """, unsafe_allow_html=True)

    # --- 1. WELCOME HERO ---
    st.markdown(f"<h1 style='font-size: 3rem; margin-bottom: 0;'>👋 Welcome back, {username}!</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #cbd5e1; font-size: 1.2rem;'>Here is what's happening on your farm today.</p>", unsafe_allow_html=True)
    
    st.markdown("---")

    # --- 2. LIVE STATUS (The Green/Red Cards) ---
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""
        <div class="stat-card" style="display: flex; align-items: center; justify-content: space-between;">
            <div>
                <h3 style="margin:0;">🌾 Active Crops</h3>
                <p style="color: #cbd5e1; margin:0;">Rice (Sona Masoori), Potato</p>
            </div>
            <div style="font-size: 2.5rem;">🚜</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="stat-card" style="display: flex; align-items: center; justify-content: space-between; border-color: #34d399;">
            <div>
                <h3 style="margin:0; color: #34d399;">🛡️ System Status</h3>
                <p style="color: #cbd5e1; margin:0;">AI Model Online & Ready</p>
            </div>
            <div style="font-size: 2.5rem;">✅</div>
        </div>
        """, unsafe_allow_html=True)

    # --- 3. COMPANY ACHIEVEMENTS (Grid Layout) ---
    st.markdown('<div class="section-title">🚀 Our Impact</div>', unsafe_allow_html=True)
    
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

    # --- 4. FARMER REVIEWS ---
    st.markdown('<div class="section-title">💬 What Farmers Say</div>', unsafe_allow_html=True)
    
    rc1, rc2 = st.columns(2)
    
    with rc1:
        st.markdown("""
        <div class="review-card">
            <div class="review-text">"I used to lose 30% of my potato crop to Blight every year. AgriDetect diagnosed it early, and the suggested spray saved my harvest!"</div>
            <div class="review-author">👤 Ramesh Reddy <span style="font-weight:normal; color:#64748b; font-size:0.9rem;">(Warangal)</span></div>
        </div>
        <div class="review-card">
            <div class="review-text">"The interface is so simple, even my father can use it. The Telugu language support would be great in the future!"</div>
            <div class="review-author">👤 Sita Lakshmi <span style="font-weight:normal; color:#64748b; font-size:0.9rem;">(Karimnagar)</span></div>
        </div>
        """, unsafe_allow_html=True)
        
    with rc2:
        st.markdown("""
        <div class="review-card">
            <div class="review-text">"Government schemes section is very helpful. I didn't know I was eligible for the PM-Kisan subsidy until I checked here."</div>
            <div class="review-author">👤 Krishna Rao <span style="font-weight:normal; color:#64748b; font-size:0.9rem;">(Nalgonda)</span></div>
        </div>
        <div class="review-card">
            <div class="review-text">"Best app for Rice Blast detection. The chemical dosage recommendations are very accurate."</div>
            <div class="review-author">👤 Venkat Goud <span style="font-weight:normal; color:#64748b; font-size:0.9rem;">(Khammam)</span></div>
        </div>
        """, unsafe_allow_html=True)

    # --- 5. FOOTER ---
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
            © 2026 AgriDetect Solutions Pvt Ltd. <br>
            Designed with ❤️ for Indian Farmers.
        </p>
    </div>
    """, unsafe_allow_html=True)