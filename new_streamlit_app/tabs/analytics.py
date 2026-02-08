import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def show():
    # --- CUSTOM CSS ---
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

    st.markdown("<h1 style='text-align: center;'>📊 Farm <span style='color:#34d399'>Analytics</span></h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #cbd5e1; margin-bottom: 30px;'>Real-time insights on crop health and yield predictions.</p>", unsafe_allow_html=True)

    # --- KPI SECTION ---
    k1, k2, k3, k4 = st.columns(4)
    with k1: st.markdown('<div class="kpi-card"><div class="kpi-label">Total Scans</div><div class="kpi-value">1,248</div><div style="color: #34d399; font-size: 0.8rem;">▲ 12% this week</div></div>', unsafe_allow_html=True)
    with k2: st.markdown('<div class="kpi-card"><div class="kpi-label">Avg Health Score</div><div class="kpi-value">87%</div><div style="color: #34d399; font-size: 0.8rem;">Stable</div></div>', unsafe_allow_html=True)
    with k3: st.markdown('<div class="kpi-card"><div class="kpi-label">Disease Alerts</div><div class="kpi-value" style="color: #f87171;">14</div><div style="color: #f87171; font-size: 0.8rem;">Requires Action</div></div>', unsafe_allow_html=True)
    with k4: st.markdown('<div class="kpi-card"><div class="kpi-label">Est. Yield</div><div class="kpi-value">4.2T</div><div style="color: #fbbf24; font-size: 0.8rem;">Potato & Rice</div></div>', unsafe_allow_html=True)

    st.write("") # Spacer

    # --- DATA PREP ---
    yield_data = pd.DataFrame({"Crop": ["Rice", "Potato", "Wheat", "Tomato"], "Yield (Tons)": [45, 60, 30, 25]})
    trend_data = pd.DataFrame({"Month": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"], "Healthy": [80, 85, 82, 88, 90, 87], "Diseased": [20, 15, 18, 12, 10, 13]})

    # --- CHARTS SECTION ---
    c1, c2 = st.columns(2)
    
    with c1:
        st.markdown("### 🌾 Crop Yield Forecast")
        fig_yield = px.bar(yield_data, x="Crop", y="Yield (Tons)", color="Crop", color_discrete_sequence=["#34d399", "#22d3ee", "#fbbf24", "#f87171"])
        
        # FIX: Apply the 'Card' background color directly to the chart since we removed the wrapper div
        fig_yield.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", 
            paper_bgcolor="rgba(255, 255, 255, 0.05)", # Glass effect inside chart
            font=dict(color="white"), 
            showlegend=False, 
            xaxis=dict(showgrid=False), 
            yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.1)"),
            margin=dict(l=20, r=20, t=20, b=20)
        )
        st.plotly_chart(fig_yield, use_container_width=True)

    with c2:
        st.markdown("### 📉 Disease Trends (6 Months)")
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(x=trend_data["Month"], y=trend_data["Healthy"], fill='tozeroy', mode='lines', name='Healthy', line=dict(width=3, color='#34d399')))
        fig_trend.add_trace(go.Scatter(x=trend_data["Month"], y=trend_data["Diseased"], fill='tozeroy', mode='lines', name='Diseased', line=dict(width=3, color='#f87171')))
        
        # FIX: Apply the 'Card' background color directly to the chart
        fig_trend.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", 
            paper_bgcolor="rgba(255, 255, 255, 0.05)", # Glass effect inside chart
            font=dict(color="white"), 
            legend=dict(orientation="h", y=1.1), 
            xaxis=dict(showgrid=False), 
            yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.1)"),
            margin=dict(l=20, r=20, t=20, b=20)
        )
        st.plotly_chart(fig_trend, use_container_width=True)

    # --- RECENT REPORTS (HTML Table is self-contained, so wrapper is fine here) ---
    st.markdown("### 📋 Recent Field Reports")
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