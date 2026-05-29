import streamlit as st
import yfinance as yf
import pandas as pd

# 1. Page Configuration
st.set_page_config(page_title="Investment Alarm Bell v2.4", layout="wide")

# Custom CSS for styling
st.markdown("""
    <style>
    .reportview-container { background: #0e1117; }
    .risk-box {
        padding: 20px;
        border-radius: 10px;
        border: 2px solid #4e4e4e;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🚨 Investment Audit & Portfolio Command Center (v2.4)")

# --- 2. DYNAMIC PORTFOLIO MANAGEMENT (from v2.2) ---
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = ["MU", "WDC", "MRVL", "NVT", "STX", "VRT", "ASML", "ANET", "GEV"]

st.sidebar.header("📈 Portfolio Management")
new_ticker = st.sidebar.text_input("Add Ticker (e.g. NVDA, TSLA):").upper()
if st.sidebar.button("Add to Watchlist"):
    if new_ticker and new_ticker not in st.session_state.portfolio:
        st.session_state.portfolio.append(new_ticker)
        st.rerun()

if st.sidebar.button("Clear Custom Stocks"):
    st.session_state.portfolio = ["MU", "WDC", "MRVL", "NVT", "STX", "VRT", "ASML", "ANET", "GEV"]
    st.rerun()

# --- 3. DATA FETCHING ENGINE ---
@st.cache_data(ttl=3600)
def fetch_all_data(portfolio_list):
    macro_tickers = {
        "Brent": "BZ=F", 
        "10Y": "^TNX", 
        "VIX": "^VIX", 
        "SPY": "^GSPC", 
        "SOX": "^SOX"
    }
    all_to_fetch = list(macro_tickers.values()) + portfolio_list
    # Download data with error handling
    try:
        raw_data = yf.download(all_to_fetch, period="250d", interval="1d", progress=False)['Close']
        # Forward fill any NaN values from missing data (pandas 2.0+ compatible)
        raw_data = raw_data.ffill().bfill()
        return raw_data, macro_tickers
    except Exception as e:
        st.error(f"Failed to fetch data: {e}")
        return None, macro_tickers

# Load data
prices, m_map = fetch_all_data(st.session_state.portfolio)
if prices is None:
    st.error("Cannot proceed without market data. Please check your tickers and try again.")
    st.stop()

# --- 4. SIDEBAR MANUAL INPUTS ---
st.sidebar.divider()
st.sidebar.header("📊 Economic Reality Check")
claims = st.sidebar.number_input("Jobless Claims (4-wk avg)", value=203750)
unemployment = st.sidebar.number_input("Unemployment Rate (%)", value=4.3)
spreads = st.sidebar.number_input("High Yield Spreads (%)", value=2.8)
capex_cut = st.sidebar.toggle("Hyperscaler CapEx Reductions?", value=False)
lead_times = st.sidebar.selectbox("HBM Lead Times", ["Rising/Stable", "Shrinking Rapidly"])
btb_ratio = st.sidebar.slider("ASML Book-to-Bill Ratio", 0.5, 2.0, 1.2)

# --- 5. RISK ENGINE LOGIC ---
m_score = 0
a_score = 0

# Macro Calculations
current_brent = prices[m_map['Brent']].iloc[-1]
current_10y = prices[m_map['10Y']].iloc[-1]
current_vix = prices[m_map['VIX']].iloc[-1]
current_spy = prices[m_map['SPY']].iloc[-1]
spy_200 = prices[m_map['SPY']].rolling(200).mean().iloc[-1]

if current_brent > 115 and current_10y > 4.75: m_score += 2
elif current_brent > 100: m_score += 1
if unemployment >= 4.5: m_score += 2
elif claims > 240000: m_score += 1
if spreads > 5.0: m_score += 2
elif spreads > 4.5: m_score += 1
if current_10y > 5.0: m_score += 2
elif current_10y > 4.5: m_score += 1
if current_spy < spy_200: m_score += 2
if current_vix > 25: m_score += 2
elif current_vix > 20: m_score += 1

# AI Calculations
sox_curr = prices[m_map['SOX']].iloc[-1]
sox_50 = prices[m_map['SOX']].rolling(50).mean().iloc[-1]
sox_200 = prices[m_map['SOX']].rolling(200).mean().iloc[-1]

if spreads > 5.0: a_score += 3 # Volatility Tax
elif spreads > 4.5: a_score += 1
if capex_cut: a_score += 2
if lead_times == "Shrinking Rapidly": a_score += 1
if btb_ratio < 1.0: a_score += 2
if sox_curr < sox_50: a_score += 1
if sox_curr < sox_200: a_score += 2

# --- 6. DISPLAY LAYOUT ---
col1, col2 = st.columns(2)

with col1:
    m_color = "green" if m_score <= 3 else "orange" if m_score <= 6 else "red"
    st.markdown(f"### 🌍 Macro Risk Assessment: <span style='color:{m_color}'>{m_score}/12</span>", unsafe_allow_html=True)
    
    with st.expander("1. Energy & Inflation Pressure"):
        st.write(f"**Current Brent:** ${current_brent:.2f}")
        st.write(f"**Current 10Y Yield:** {current_10y:.2f}%")
        st.info("Assessment: Energy + rates together represent a double squeeze on both consumers and valuations.")
        
    with st.expander("2. Labor Market Deterioration"):
        st.write(f"**Claims:** {claims:,} | **Unemployment:** {unemployment}%")
        st.info("Assessment: Labor is a lagging but decisive trigger—once it rolls over, recession is highly probable.")

    with st.expander("3. Credit & Liquidity Risk"):
        st.write(f"**HY Spreads:** {spreads}%")
        st.info("Assessment: Credit markets lead equities. Spreads signal tightening liquidity.")

    with st.expander("4. Technical Trend & Structure"):
        st.write(f"**S&P 500:** {current_spy:.0f} (200-DMA: {spy_200:.0f})")
        st.info("Assessment: Confirms whether weakness is broad-based vs isolated.")

with col2:
    a_color = "green" if a_score <= 3 else "orange" if a_score <= 6 else "red"
    st.markdown(f"### 🤖 AI Infra Cycle Risk: <span style='color:{a_color}'>{a_score}/10</span>", unsafe_allow_html=True)

    with st.expander("1. CapEx Pulse (Hyperscalers)"):
        st.write(f"**Status:** {'Guidance Cuts Detected' if capex_cut else 'Aggressive Build Continues'}")
        st.info("Assessment: AI stocks trade on Hyperscaler spending. Efficiency talk = Multiple compression.")

    with st.expander("2. Semi Inventory & Lead Times"):
        st.write(f"**HBM Leads:** {lead_times} | **ASML BTB:** {btb_ratio}")
        st.info("Assessment: Shrinking lead times signal peak demand has passed.")

    with st.expander("3. Technical Health (Semis)"):
        st.write(f"**SOX Index:** {sox_curr:.0f}")
        st.write(f"**Trend:** {'✅ Above 50-DMA' if sox_curr > sox_50 else '🚨 Below 50-DMA'}")
        st.info("Assessment: Semis must lead. A week below the 50-DMA is a major warning.")

# --- 7. COMPOSITE RISK SCORE BOX ---
st.divider()
total_risk = m_score + a_score
st.subheader("📊 Integrated Composite Risk Score")
score_col1, score_col2 = st.columns([1, 2])

with score_col1:
    st.metric("Total Score", f"{total_risk} / 22")

with score_col2:
    if total_risk <= 6:
        st.success("✅ LOW RISK: Stay invested. Use dips to add to core AI holdings.")
    elif total_risk <= 12:
        st.warning("⚠️ MODERATE: Trim high-beta names. Move stops to lock-in profit.")
    else:
        st.error("🚨 HIGH RISK: Rotate to cash/defensives. The 'AI Premium' is evaporating.")

# --- 8. PORTFOLIO 'LINE IN THE SAND' (Fixed Logic) ---
st.header("🛡️ Portfolio 'Line in the Sand' Tracker")
p_table = []
for s in st.session_state.portfolio:
    try:
        # Accessing the column directly from the prices dataframe
        if s not in prices.columns:
            p_table.append({"Ticker": s, "Current Price": "Ticker not found", "Stop Loss (15%)": "-", "200-DMA": "-", "Status": "❌ Invalid Ticker"})
            continue
            
        curr = prices[s].iloc[-1]
        ma200 = prices[s].rolling(200).mean().iloc[-1]
        
        # Check for NaN values
        if pd.isna(curr) or pd.isna(ma200):
            p_table.append({"Ticker": s, "Current Price": "Data Pending", "Stop Loss (15%)": "-", "200-DMA": "-", "Status": "⏳ No Data"})
            continue
            
        stop_loss = curr * 0.85 # 15% Buffer
        
        p_table.append({
            "Ticker": s,
            "Current Price": f"${curr:.2f}",
            "Stop Loss (15%)": f"${stop_loss:.2f}",
            "200-DMA": f"${ma200:.2f}",
            "Status": "✅ Healthy" if curr > ma200 else "⚠️ Below 200-DMA"
        })
    except Exception as e:
        # If a newly added ticker isn't ready yet
        p_table.append({"Ticker": s, "Current Price": f"Error: {str(e)}", "Stop Loss (15%)": "-", "200-DMA": "-", "Status": "⚠️ Error"})

st.table(pd.DataFrame(p_table))

# --- 9. BULL MARKET FLASH SALE LOGIC ---
if total_risk <= 6 and spreads < 4.0:
    st.info("💡 **Bull Market 'Buy Opportunity' Flag:** Total risk is low. If a stock hits its stop-loss now, it is likely a 'Flash Sale'. Consider selling only half.")
