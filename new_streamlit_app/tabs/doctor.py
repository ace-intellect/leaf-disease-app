import streamlit as st
import numpy as np
from PIL import Image
import time
import base64
from io import BytesIO
import os
import sys
import json

# --- BACKEND CONNECTION ---
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
root_dir = os.path.dirname(parent_dir)
sys.path.append(parent_dir)

from model_loader import load_model, predict_image
from preprocess import preprocess_image

def image_to_base64(image):
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

def show():
    # --- CSS ---
    st.markdown("""
    <style>
    /* 1. UPLOAD BUTTON STYLE (Grey/Glass) */
    [data-testid="stFileUploader"] button {
        background: rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        font-weight: 600 !important;
    }
    [data-testid="stFileUploader"] button:hover {
        background: rgba(255, 255, 255, 0.2) !important;
        border-color: #34d399 !important;
        color: #34d399 !important;
    }
    
    /* 2. FORCE WHITE TEXT */
    [data-testid="stFileUploader"] { color: white !important; }
    [data-testid="stFileUploader"] small { color: #e2e8f0 !important; }
    [data-testid="stFileUploader"] span { color: white !important; }
    
    /* 3. UPLOAD ZONE */
    [data-testid="stFileUploader"] section {
        background-color: rgba(255, 255, 255, 0.05);
        border: 2px dashed rgba(52, 211, 153, 0.5);
    }

    /* 4. ANIMATIONS */
    @keyframes popIn { 0% { opacity: 0; transform: translateY(50px) scale(0.9); } 100% { opacity: 1; transform: translateY(0) scale(1); } }
    @keyframes scan { 0% { top: 0%; opacity: 0; } 20% { opacity: 1; } 80% { opacity: 1; } 100% { top: 100%; opacity: 0; } }
    
    .scan-container { position: relative; overflow: hidden; border-radius: 15px; line-height: 0; }
    .scan-beam { position: absolute; width: 100%; height: 4px; background: rgba(52, 211, 153, 0.9); box-shadow: 0 0 15px #34d399; animation: scan 2.5s infinite linear; z-index: 10; top: 0; left: 0; }

    /* PREVIEW CARD */
    .preview-glass {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 20px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 20px 50px rgba(0,0,0,0.5);
        text-align: center;
        margin-top: 20px;
    }

    /* RESULT CARD */
    .result-glass {
        background: linear-gradient(135deg, rgba(255,255,255,0.1), rgba(255,255,255,0.05));
        backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 40px;
        border-left: 6px solid #34d399;
        margin-top: 40px;
        box-shadow: 0 25px 60px rgba(0,0,0,0.5);
        animation: popIn 0.8s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
    }
    
    /* ANALYZE BUTTON (Keep Green for Emphasis) */
    .stButton button {
        background: linear-gradient(90deg, #22d3ee, #34d399) !important;
        color: #020617 !important;
        font-weight: 800;
        border-radius: 50px;
    }
    h1, h2, h3, h4, h5, p, div { color: white !important; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<h1 style='text-align: center; margin-bottom: 10px;'>🩺 AI Plant <span style='color:#34d399'>Doctor</span></h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #cbd5e1; margin-bottom: 40px;'>Upload a leaf image for instant diagnosis.</p>", unsafe_allow_html=True)

    config_path = os.path.join(root_dir, "config", "model_config.json")
    if os.path.exists(config_path):
        with open(config_path) as f:
            config = json.load(f)
        selected_model_name = list(config['models'].keys())[0]
        model, model_type = load_model(selected_model_name)
    else:
        st.error(f"⚠️ Config missing at {config_path}")
        return

    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        uploaded_file = st.file_uploader("Upload Image", type=["jpg", "png", "jpeg"], label_visibility="collapsed")

    if uploaded_file:
        image = Image.open(uploaded_file)
        img_b64 = image_to_base64(image)
        
        col_p1, col_p2, col_p3 = st.columns([1, 1, 1])
        
        with col_p2:
            st.markdown(f"""
            <div class="preview-glass">
                <div class="scan-container">
                    <div class="scan-beam"></div>
                    <img src="data:image/png;base64,{img_b64}" style="width: 100%; border-radius: 15px; display: block;">
                </div>
                <p style="margin-top: 15px; color: #94a3b8; font-size: 0.9rem;">Scanning Leaf Details...</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Analyze Button
            if st.button("🚀 Analyze Now"):
                if model:
                    with st.spinner("🔬 AI is analyzing cell structure..."):
                        try:
                            time.sleep(1.5)
                            processed_img = preprocess_image(image, model_type)
                            predictions = predict_image(model, model_type, processed_img)
                            class_indices = config['models'][selected_model_name]['classes']
                            idx = np.argmax(predictions)
                            confidence = float(np.max(predictions) * 100)
                            result = class_indices.get(str(idx), f"Class {idx}")
                            st.session_state.ai_result = (result, confidence)
                        except Exception as e:
                            st.error(f"Prediction Error: {e}")
                else:
                    st.error("⚠️ AI Model not connected.")

    if 'ai_result' in st.session_state and uploaded_file:
        res, conf = st.session_state.ai_result
        is_healthy = "healthy" in res.lower()
        color = "#34d399" if is_healthy else "#ef4444"
        icon = "🌿" if is_healthy else "🦠"

        r1, r2, r3 = st.columns([1, 2, 1])
        with r2:
            st.markdown(f"""
            <div class="result-glass" style="border-left-color: {color};">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <h4 style="margin:0; color: #94a3b8; letter-spacing: 2px; font-size: 0.8rem;">DIAGNOSIS COMPLETE</h4>
                        <h2 style="margin:5px 0 0 0; font-size: 2.2rem; color: white;">{res.replace('_', ' ')}</h2>
                    </div>
                    <div style="font-size: 3rem; background: rgba(255,255,255,0.05); padding: 15px; border-radius: 50%; border: 1px solid rgba(255,255,255,0.1);">{icon}</div>
                </div>
                <div style="margin-top: 25px;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                        <span style="color: #cbd5e1;">Confidence</span>
                        <span style="color: {color}; font-weight: bold;">{conf:.1f}%</span>
                    </div>
                    <div style="width: 100%; background: rgba(255,255,255,0.1); height: 8px; border-radius: 10px;">
                        <div style="width: {conf}%; background: {color}; height: 100%; border-radius: 10px;"></div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            if not is_healthy:
                st.markdown(f"""
                <div class="result-glass" style="border-left-color: #f59e0b; margin-top: 20px; animation-delay: 0.2s;">
                    <h3 style="color: #f59e0b; margin-top: 0;">💊 Recommended Treatment</h3>
                    <ul style="color: #cbd5e1; line-height: 1.8; font-size: 1rem; padding-left: 20px;">
                        <li><b>Chemical:</b> Apply Mancozeb.</li>
                        <li><b>Action:</b> Isolate plant immediately.</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.balloons()