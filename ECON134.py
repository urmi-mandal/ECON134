import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(
    page_title="Rolling Back the WACC", 
    layout="wide", 
    page_icon="🛒"
)

st.markdown("""
    <style>
    .stApp { background-color: #00031c; color: white; }
    
    div[data-testid="stMetricValue"] { 
        font-size: 40px; 
        font-weight: bold;
        color: #00f2fe; 
        text-shadow: 0px 0px 12px rgba(0, 242, 254, 0.5); 
    }
    
    .stSlider > div > div > div > div { 
        background: linear-gradient(90deg, #ff00c1 0%, #00f2fe 100%); 
    }
    </style>
    """, unsafe_allow_html=True)

MARKET_PRICE = 126.28  
SHARES_OUT = 7.97      
BASE_FCF = 14.92       
NET_DEBT = 56.37       
TARGET_GROWTH = 28.9   

st.title("🛒 Shopping For The Real Price of Walmart: A Game")
st.markdown("<p style='color: white; font-size: 16px; margin-top: -10px;'>Urmi Mandal - ECON 134</p>", unsafe_allow_html=True)

col1, col2 = st.columns([1, 1.2], gap="large")

with col1:
    st.markdown("<h3 style='color: white;'>Adjust Your Assumptions!</h3>", unsafe_allow_html=True)
    level = st.selectbox(
        "Select Scenario Override",
        options=["Urmi's Assumptions", "Bear Case (Pessimistic)", "Market Optimist", "CFO's Hopes"],
        index=0
    )

    if level == "Bear Case (Pessimistic)":
        w_init, g_init, tg_init = 6.52, 10.0, 1.0 
    elif level == "Urmi's Assumptions":
        w_init, g_init, tg_init = 6.31, 21.25, 2.0 
    elif level == "Market Optimist":
        w_init, g_init, tg_init = 6.11, 28.9, 3.0 
    elif level == "CFO's Hopes":
        w_init, g_init, tg_init = 5.00, 35.0, 3.5 
    else:
        w_init, g_init, tg_init = 6.31, 21.25, 2.0

    st.markdown("<h3 style='color: white;'>Economic Levers</h3>", unsafe_allow_html=True)
    wacc = st.slider("Cost of Capital (WACC) %", 4.0, 10.0, float(w_init), step=0.01) / 100
    fcf_growth = st.slider("5-Year FCF Growth %", 0.0, 45.0, float(g_init), step=0.1) / 100
    t_growth = st.slider("Terminal Growth Rate %", 0.5, 4.0, float(tg_init), step=0.1) / 100

years = np.array([1, 2, 3, 4, 5])
projected_fcf = BASE_FCF * (1 + fcf_growth)**years
pv_fcf = projected_fcf / (1 + wacc)**years

terminal_val = (projected_fcf[-1] * (1 + t_growth)) / (wacc - t_growth)
pv_terminal = terminal_val / (1 + wacc)**5

enterprise_value = pv_fcf.sum() + pv_terminal
intrinsic_price = (enterprise_value - NET_DEBT) / SHARES_OUT 

upside = ((intrinsic_price / MARKET_PRICE) - 1) * 100

if upside > 5:
    signal = "Buy"
elif upside < -5:
    signal = "Sell"
else:
    signal = "Hold"

with col2:
    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("Your Intrinsic Value", f"${intrinsic_price:.2f}")
    with m2:
        st.metric("Market Price", f"${MARKET_PRICE}")
    with m3:
        st.metric(signal, f"{upside:.1f}%")

    st.info("**Challenge: Match the Market**\n\nCan you find the exact growth rate that justifies the current market price of $126.28?")

gauge_max = max(200, intrinsic_price * 1.2)

fig = go.Figure(go.Indicator(
    mode = "gauge+number+delta",
    value = intrinsic_price,
    domain = {'x': [0, 1], 'y': [0, 1]},
    title = {'text': "Intrinsic Value vs Market", 'font': {'size': 20, 'color': "white"}},
    delta = {'reference': MARKET_PRICE, 'increasing': {'color': "#00ffcc"}, 'decreasing': {'color': "#ff0066"}},
    gauge = {
        'axis': {'range': [None, gauge_max], 'tickwidth': 2, 'tickcolor': "white"},
        'bar': {'color': "#00f2fe"},
        'bgcolor': "rgba(0,0,0,0)",
        'borderwidth': 0,
        'steps': [
            {'range': [0, MARKET_PRICE], 'color': 'rgba(255, 0, 102, 0.2)'},
            {'range': [MARKET_PRICE, gauge_max], 'color': 'rgba(0, 242, 254, 0.2)'}],
        'threshold': {
            'line': {'color': "#ffffff", 'width': 5},
            'thickness': 0.75,
            'value': MARKET_PRICE}
    }
))
fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font={'color': "white"}, height=350, margin=dict(l=20, r=20, t=50, b=20))
st.plotly_chart(fig, use_container_width=True)

if upside > 5:
    st.success(f"**System Analysis: BUY SIGNAL.** Model shows {upside:.1f}% upside. The stock is currently undervalued.")
elif upside < -5:
    st.warning(f"**System Analysis: SELL SIGNAL.** Model shows {abs(upside):.1f}% Downside. The stock is currently overvalued.")
else:
    st.info(f"**System Analysis: HOLD SIGNAL.** Market is priced perfectly to your model.")

with st.expander("📂 Detailed Cash Flow Projections"):
    df = pd.DataFrame({
        "Year": [2027, 2028, 2029, 2030, 2031],
        "Projected FCF ($B)": projected_fcf.round(2),
        "Present Value ($B)": pv_fcf.round(2)
    })
    st.dataframe(df.set_index("Year"), use_container_width=True)