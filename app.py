import streamlit as st
import yfinance as yf
import pandas as pd

# Set page config for mobile
st.set_page_config(page_title="Investment Alarm Bell", layout="centered")

st.title("🚨 Investment Audit v2.1")
st.subheader("Macro & AI Infrastructure Risk Dashboard")

# --- DATA FETCHING ---
@st.cache_data(ttl=3600)
def get_market_data():
    tickers = {
        "Brent Crude": "BZ=F",
        "US 10Y Yield": "^TNX",
        "VIX": "^VIX",
        "S&P 500": "^GSPC",
        "SOX (Semis)": "^SOX",
        "NVDA": "NVDA",
        "MSFT": "MSFT"
    }
    data = {}
    for name, ticker in tickers.items():
        try:
            t = yf.Ticker(ticker)
            hist = t.history(period="250d")
            data[name] = {
                "current": hist['Close'].iloc[-1],
                "dma200": hist['Close'].rolling(window=200).mean().iloc[-1],
                "dma50": hist['Close'].rolling(window=50).mean().iloc[-1],
                "prev_close": hist['Close'].iloc[-2]
            }
        except:
            # Fallback for data gaps
            data[name] = {"current": 0, "dma200": 0, "dma50": 0, "prev_close": 0}
    return data

market = get_market_data()

# --- USER INPUTS (For Economic Data not easily automated) ---
st.sidebar.header("Manual Economic Inputs")
jobless_claims = st.sidebar.number_input("Weekly Jobless Claims", value=225000)
unemployment_rate = st.sidebar.number_input("Unemployment Rate (%)", value=3.9, step=0.1)
hy_spreads = st.sidebar.number_input("High Yield Spreads (%)", value=3.5, step=0.1)
capex_cut = st.sidebar.toggle("Have 2+ Hyperscalers cut CapEx?")

# --- SCORE CALCULATION LOGIC ---
macro_score = 0
ai_score = 0

# 1. Macro Logic
if market["Brent Crude"]["current"] > 115 and market["US 10Y Yield"]["current"] > 4.75: macro_score += 2
elif market["Brent Crude"]["current"] > 100: macro_score += 1

if unemployment_rate >= 4.5: macro_score += 2
elif jobless_claims > 240000: macro_score += 1

if hy_spreads > 5.0: macro_score += 2
elif hy_spreads > 4.5: macro_score += 1

if market["US 10Y Yield"]["current"] > 5.0: macro_score += 2
elif market["US 10Y Yield"]["current"] > 4.5: macro_score += 1

if market["S&P 500"]["current"] < market["S&P 500"]["dma200"]: macro_score += 2

if market["VIX"]["current"] > 25: macro_score += 2
elif market["VIX"]["current"] > 20: macro_score += 1

# 2. AI Infrastructure Logic
if hy_spreads > 5.0: ai_score += 3 # Includes the "Volatility Tax"
elif hy_spreads > 4.5: ai_score += 1

if capex_cut: ai_score += 2

if market["SOX (Semis)"]["current"] < market["SOX (Semis)"]["dma50"]: ai_score += 1
if market["SOX (Semis)"]["current"] < market["SOX (Semis)"]["dma200"]: ai_score += 2

# --- DISPLAY ---
col1, col2 = st.columns(2)

with col1:
    st.metric("Macro Score", f"{macro_score}/12")
    if macro_score <= 3: st.success("Risk-On")
    elif macro_score <= 6: st.warning("Trim Positions")
    elif macro_score <= 9: st.error("Hedge Aggressively")
    else: st.markdown("🔴 **CAPITAL PRESERVATION**")

with col2:
    st.metric("AI Risk Score", f"{ai_score}/10")
    if ai_score <= 3: st.success("Stay Invested")
    elif ai_score <= 6: st.warning("Move Stops to BE")
    else: st.error("Rotate to Cash")

st.divider()

# Action Framework Table
st.header("⚙️ Recommended Action")
combined_risk = "Low" if (macro_score + ai_score) < 6 else "Moderate" if (macro_score + ai_score) < 12 else "High"
action_map = {
    "Low": "Stay invested. Use dips to add to winners.",
    "Moderate": "Trim high-beta names. Lock in profits.",
    "High": "Rotate to cash/defensives. The 'AI Premium' is evaporating."
}
st.info(f"**Current Stance:** {combined_risk}\n\n**Action:** {action_map[combined_risk]}")

# Market Data Reference
with st.expander("View Live Market Data"):
    st.write(f"Brent Crude: ${market['Brent Crude']['current']:.2f}")
    st.write(f"US 10Y Yield: {market['US 10Y Yield']['current']:.2f}%")
    st.write(f"VIX: {market['VIX']['current']:.2f}")
    st.write(f"S&P 500 vs 200DMA: {market['S&P 500']['current']:.0f} / {market['S&P 500']['dma200']:.0f}")
