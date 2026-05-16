import streamlit as st
import yfinance as yf
import pandas as pd

# Page Config
st.set_page_config(page_title="Investment Alarm Bell v2.3", layout="wide")

# --- CUSTOM CSS FOR BOXES ---
st.markdown("""
    <style>
    .reportview-container { background: #0e1117; }
    .risk-box {
        padding: 20px;
        border-radius: 10px;
        border: 2px solid #4e4e4e;
        margin-bottom: 20px;
    }
    .macro-bg { background-color: #1a2a3a; border-color: #3498db; }
    .ai-bg { background-color: #2a1a3a; border-color: #9b59b6; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚨 Weekly Investment “Alarm Bell” Audit (v2.3)")

# --- 1. LIVE DATA FETCHING ---
@st.cache_data(ttl=3600)
def fetch_data():
    tickers = {
        "Brent": "BZ=F", "10Y": "^TNX", "VIX": "^VIX", 
        "SPY": "^GSPC", "SOX": "^SOX", "MU": "MU", 
        "VRT": "VRT", "ASML": "ASML", "NVT": "NVT"
    }
    data = yf.download(list(tickers.values()), period="250d", interval="1d")['Close']
    return data, tickers

prices, ticker_map = fetch_data()

# --- 2. SIDEBAR / MANUAL INPUTS (May 2026 Context) ---
st.sidebar.header("📊 Economic Reality Check")
claims = st.sidebar.number_input("Jobless Claims (4-wk avg)", value=203750)
unemployment = st.sidebar.number_input("Unemployment Rate (%)", value=4.3)
spreads = st.sidebar.number_input("High Yield Spreads (%)", value=2.8)
capex_cut = st.sidebar.toggle("Hyperscaler CapEx Reductions?", value=False)
lead_times = st.sidebar.selectbox("HBM Lead Times", ["Rising/Stable", "Shrinking Rapidly"])
btb_ratio = st.sidebar.slider("ASML Book-to-Bill Ratio", 0.5, 2.0, 1.2)

# --- 3. RISK ENGINE LOGIC ---
m_score = 0
a_score = 0

# Macro Triggers
if prices[ticker_map['Brent']].iloc[-1] > 115 and prices[ticker_map['10Y']].iloc[-1] > 4.75: m_score += 2
elif prices[ticker_map['Brent']].iloc[-1] > 100: m_score += 1

if unemployment >= 4.5: m_score += 2
elif claims > 240000: m_score += 1

if spreads > 5.0: m_score += 2
elif spreads > 4.5: m_score += 1

if prices[ticker_map['10Y']].iloc[-1] > 5.0: m_score += 2
elif prices[ticker_map['10Y']].iloc[-1] > 4.5: m_score += 1

spy_curr = prices[ticker_map['SPY']].iloc[-1]
spy_200 = prices[ticker_map['SPY']].rolling(200).mean().iloc[-1]
if spy_curr < spy_200: m_score += 2

vix_curr = prices[ticker_map['VIX']].iloc[-1]
if vix_curr > 25: m_score += 2
elif vix_curr > 20: m_score += 1

# AI Triggers
if spreads > 5.0: a_score += 3  # Volatility Tax included
elif spreads > 4.5: a_score += 1

if capex_cut: a_score += 2
if lead_times == "Shrinking Rapidly": a_score += 1
if btb_ratio < 1.0: a_score += 2

sox_curr = prices[ticker_map['SOX']].iloc[-1]
sox_50 = prices[ticker_map['SOX']].rolling(50).mean().iloc[-1]
sox_200 = prices[ticker_map['SOX']].rolling(200).mean().iloc[-1]
if sox_curr < sox_50: a_score += 1
if sox_curr < sox_200: a_score += 2

# --- 4. DISPLAY LAYOUT ---
col1, col2 = st.columns(2)

with col1:
    # Color-coded Macro Header
    m_color = "green" if m_score <= 3 else "orange" if m_score <= 6 else "red"
    st.markdown(f"### 🌍 Macro Risk Assessment: <span style='color:{m_color}'>{m_score}/12</span>", unsafe_allow_html=True)
    
    with st.expander("1. Energy & Inflation"):
        st.write(f"**Brent Crude:** ${prices[ticker_map['Brent']].iloc[-1]:.2f}")
        st.info("Assessment: Energy + rates together represent a double squeeze on both consumers and valuations.")
        
    with st.expander("2. Labor Market"):
        st.write(f"**Status:** {claims:,} Claims | {unemployment}% Unemp.")
        st.info("Assessment: Decisive trigger—once labor rolls over, recession risk becomes highly probable.")

    with st.expander("3. Credit & Liquidity"):
        st.write(f"**HY Spreads:** {spreads}%")
        st.info("Assessment: Credit markets lead equities. Rapid spread expansion signals tightening liquidity.")

    with st.expander("4. Technical Trend"):
        st.write(f"**S&P 500:** {spy_curr:.0f} (200-DMA: {spy_200:.0f})")
        st.info("Assessment: Confirms whether weakness is broad-based vs isolated.")

with col2:
    # Color-coded AI Header
    a_color = "green" if a_score <= 3 else "orange" if a_score <= 6 else "red"
    st.markdown(f"### 🤖 AI Infra Cycle Risk: <span style='color:{a_color}'>{a_score}/10</span>", unsafe_allow_html=True)

    with st.expander("1. Hyperscaler CapEx"):
        st.write(f"**Guidance Status:** {'CUT' if capex_cut else 'Aggressive Build'}")
        st.info("Assessment: AI stocks trade on hyperscaler spending. Guidance cuts end the trade.")

    with st.expander("2. Semi Inventory"):
        st.write(f"**HBM Lead Times:** {lead_times}")
        st.write(f"**ASML Book-to-Bill:** {btb_ratio}")
        st.info("Assessment: Shrinking lead times signal the 'Peak Demand' has passed.")

    with st.expander("3. Energy Constraints"):
        st.write("**Status:** Monitoring GE Vernova & Eaton prints.")
        st.info("Assessment: Cooling in the 'Electrification' trade signals infra bottlenecks.")

# --- 5. COMPOSITE SCORE BOX ---
st.divider()
total_risk = m_score + a_score
st.subheader("📊 Integrated Composite Risk Score")
score_col1, score_col2 = st.columns([1, 3])

with score_col1:
    st.metric("Total Score", f"{total_risk} Points")

with score_col2:
    if total_risk <= 4:
        st.success("✅ RISK-ON: Stay invested. Focus on ASML, NVT, MU.")
        if spreads < 4.0:
            st.markdown("⭐ **BULL MARKET FLAG:** If a core stock hits its Stop-Loss now, it's likely a **Flash Sale**. Consider 'Selling Half' rather than a full exit.")
    elif total_risk <= 8:
        st.warning("⚠️ CAUTION: Trim leverage. Move stop-losses to 'Break Even' or 'Lock-in Profit' levels.")
    else:
        st.error("🚨 DEFENSIVE: Liquidity is drying up. Rotate to cash; the AI Premium is evaporating.")

# --- 6. PORTFOLIO STOP-LOSS TRACKER ---
st.header("🛡️ Portfolio 'Line in the Sand'")
port_stocks = ["MU", "WDC", "MRVL", "NVT", "STX", "VRT", "ASML", "ANET", "GEV"]
p_table = []
for s in port_stocks:
    curr = prices[ticker_map.get(s, s)].iloc[-1]
    stop = curr * 0.85 # 15% Stop-Loss logic
    p_table.append({
        "Ticker": s,
        "Current Price": f"${curr:.2f}",
        "Stop Loss (15%)": f"${stop:.2f}",
        "Trend": "✅ Healthy" if curr > prices[ticker_map.get(s, s)].rolling(200).mean().iloc[-1] else "🚨 Breakdown"
    })
st.table(p_table)
