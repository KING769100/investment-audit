import streamlit as st
import yfinance as yf
import pandas as pd

# Set page config
st.set_page_config(page_title="AI & Macro Audit", layout="wide")

# --- UI HEADER ---
st.title("🚨 Investment Alarm Bell & AI Portfolio Audit")
st.markdown("""
**Objective:** This app serves as a cold-blooded decision engine. It removes emotion by forcing you to look at 
Macro Liquidity and Technical Trends. 
*   **Macro Score:** Measures systemic risk (Recession/Inflation).
*   **AI Risk Score:** Measures the specific health of the AI Infrastructure cycle.
""")

# --- PORTFOLIO MANAGEMENT ---
# Default stocks from your screenshot
default_tickers = ["MU", "WDC", "MRVL", "NVT", "STX", "VRT", "ASML", "ANET", "GEV"]

if 'portfolio' not in st.session_state:
    st.session_state.portfolio = default_tickers

st.sidebar.header("📈 Portfolio Management")
new_ticker = st.sidebar.text_input("Add Ticker (e.g. TSLA, AMD):").upper()
if st.sidebar.button("Add to Watchlist"):
    if new_ticker and new_ticker not in st.session_state.portfolio:
        st.session_state.portfolio.append(new_ticker)

# --- DATA FETCHING ---
@st.cache_data(ttl=3600)
def get_data(tickers):
    # Macro Tickers
    macro_map = {"Brent Oil": "BZ=F", "10Y Yield": "^TNX", "VIX": "^VIX", "S&P 500": "^GSPC", "Semis Index": "^SOX"}
    all_tickers = list(macro_map.values()) + tickers
    
    data = yf.download(all_tickers, period="250d", interval="1d")['Close']
    return data, macro_map

all_data, macro_map = get_data(st.session_state.portfolio)

# --- SIDEBAR INPUTS ---
st.sidebar.divider()
st.sidebar.header("Manual Economic Data")
jobless_claims = st.sidebar.number_input("Weekly Jobless Claims", value=225000)
unemployment_rate = st.sidebar.number_input("Unemployment Rate (%)", value=3.9)
hy_spreads = st.sidebar.number_input("High Yield Spreads (%)", value=3.5)
capex_cut = st.sidebar.toggle("2+ Hyperscalers cut CapEx?")

# --- CALCULATION LOGIC ---
current_brent = all_data[macro_map["Brent Oil"]].iloc[-1]
current_10y = all_data[macro_map["10Y Yield"]].iloc[-1]
current_vix = all_data[macro_map["VIX"]].iloc[-1]
current_spy = all_data[macro_map["S&P 500"]].iloc[-1]
spy_200dma = all_data[macro_map["S&P 500"]].rolling(200).mean().iloc[-1]

macro_score = 0
# Logic Engine
if current_brent > 115 and current_10y > 4.75: macro_score += 2
elif current_brent > 100: macro_score += 1

if unemployment_rate >= 4.5: macro_score += 2
elif jobless_claims > 240000: macro_score += 1

if hy_spreads > 5.0: macro_score += 2
elif hy_spreads > 4.5: macro_score += 1

if current_10y > 5.0: macro_score += 2
elif current_10y > 4.5: macro_score += 1

if current_spy < spy_200dma: macro_score += 2

if current_vix > 25: macro_score += 2
elif current_vix > 20: macro_score += 1

# --- AI RISK SCORE ---
ai_score = 0
sox_current = all_data[macro_map["Semis Index"]].iloc[-1]
sox_50dma = all_data[macro_map["Semis Index"]].rolling(50).mean().iloc[-1]
sox_200dma = all_data[macro_map["Semis Index"]].rolling(200).mean().iloc[-1]

if hy_spreads > 5.0: ai_score += 3  # The Volatility Tax
if capex_cut: ai_score += 2
if sox_current < sox_50dma: ai_score += 1
if sox_current < sox_200dma: ai_score += 2

# --- DISPLAY LAYOUT ---
col1, col2 = st.columns(2)

with col1:
    st.header("🌍 Macro Risk")
    st.metric("Macro Composite Score", f"{macro_score} / 12")
    with st.expander("See Rationale"):
        st.write("**Brent Oil:** High energy costs act as a 'tax' on consumers and raise inflation.")
        st.write("**Jobless Claims:** Labor is the lagging indicator. If it rolls, a recession is here.")
        st.write("**HY Spreads:** The 'Master Filter'. If spreads widen, nobody wants to own risky stocks.")
    
with col2:
    st.header("🤖 AI Infra Risk")
    st.metric("AI Cycle Score", f"{ai_score} / 10")
    with st.expander("See Rationale"):
        st.write("**CapEx:** AI stocks trade on the spending of MSFT/GOOGL. If they cut, the trade is over.")
        st.write("**SOX Trend:** Semis lead the market. Below the 50-day MA suggests a momentum breakdown.")

st.divider()

# --- PORTFOLIO TRACKER ---
st.header("📋 Live Portfolio Technical Health")
p_data = []
for t in st.session_state.portfolio:
    curr = all_data[t].iloc[-1]
    ma50 = all_data[t].rolling(50).mean().iloc[-1]
    ma200 = all_data[t].rolling(200).mean().iloc[-1]
    status = "✅ Healthy" if curr > ma50 else "⚠️ Caution" if curr > ma200 else "🚨 Exit Trigger"
    p_data.append({"Ticker": t, "Price": round(curr, 2), "vs 50DMA": "Above" if curr > ma50 else "Below", "Status": status})

st.table(pd.DataFrame(p_data))

# --- FINAL ACTION ---
st.divider()
total_risk = macro_score + ai_score
if total_risk <= 4:
    st.success("STANCE: FULL RISK-ON. Use dips to add to core AI holdings.")
elif total_risk <= 8:
    st.warning("STANCE: CAUTION. Tighten stop-losses. Do not add new capital.")
else:
    st.error("STANCE: CAPITAL PRESERVATION. Hedge aggressively or move to cash.")
