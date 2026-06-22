import streamlit as st
import yfinance as yf
import pandas as pd
import time
from concurrent.futures import ThreadPoolExecutor

# List of 100 NSE Stocks
all_stocks = [
    "GLENMARK.NS", "PAYTM.NS", "PREMIERENE.NS", "PRESTIGE.NS", "IREDA.NS", "CONCOR.NS", 
    "WAAREEENER.NS", "MOTILALOFS.NS", "NATIONALUM.NS", "NYKAA.NS", "POLYCAB.NS", "IDEA.NS", 
    "HDFCAMC.NS", "NMDC.NS", "KALYANKJIL.NS", "MFSL.NS", "NTPCGREEN.NS", "MANKIND.NS", 
    "SAIL.NS", "TATATECH.NS", "DIXON.NS", "OBEROIRLTY.NS", "BHARTIHEXA.NS", "ACC.NS", 
    "HUDCO.NS", "APLAPOLLO.NS", "AUBANK.NS", "JUBLFOOD.NS", "MAXHEALTH.NS", "PATANJALI.NS", 
    "TIINDIA.NS", "MPHASIS.NS", "LICHSGFIN.NS", "ATGL.NS", "EXIDEIND.NS", "TORNTPOWER.NS", 
    "SBICARD.NS", "GODREJPROP.NS", "ASTRAL.NS", "SUZLON.NS", "PETRONET.NS", "BANDHANBNK.NS", 
    "MUTHOOTFIN.NS", "RVNL.NS", "CUMMINSIND.NS", "VOLTAS.NS", "SONACOMS.NS", "IRCTC.NS", 
    "BHEL.NS", "TATAELXSI.NS", "KPITTECH.NS", "IRB.NS", "BIOCON.NS", "UNIONBANK.NS", 
    "APOLLOTYRE.NS", "YESBANK.NS", "ASHOKLEY.NS", "MARICO.NS", "TATACOMM.NS", "HINDZINC.NS", 
    "IGL.NS", "PHOENIXLTD.NS", "UPL.NS", "ABCAPITAL.NS", "INDUSTOWER.NS", "SRF.NS", 
    "GMRAIRPORT.NS", "SJVN.NS", "SUPREMEIND.NS", "PERSISTENT.NS", "COCHINSHIP.NS", "OLAELEC.NS", 
    "NHPC.NS", "MAHABANK.NS", "PAGEIND.NS", "LUPIN.NS", "LTF.NS", "MAZDOCK.NS", "AUROPHARMA.NS", 
    "IDFCFIRSTB.NS", "M&MFIN.NS", "HINDPETRO.NS", "POLICYBZR.NS", "COLPAL.NS", "FEDERALBNK.NS", 
    "BANKINDIA.NS", "ESCORTS.NS", "ABFRL.NS", "INDIANB.NS", "ALKEM.NS", "MRF.NS", "OFSS.NS", 
    "OIL.NS", "BSE.NS", "COFORGE.NS", "BHARATFORG.NS", "PIIND.NS", "SOLARINDS.NS", "BDL.NS"
]

# 1. Premium Cyberpunk Dark UI
st.set_page_config(page_title="Ultra Fast Algo Terminal", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');
    .stApp { background-color: #06090e; font-family: 'Segoe UI', sans-serif; }
    .main-title { color: #00ffcc; text-align: center; font-size: 32px; font-weight: 800; text-shadow: 0 0 15px rgba(0, 255, 204, 0.4); margin-bottom: 5px; }
    .sub-title { color: #8a99ad; text-align: center; font-size: 14px; margin-bottom: 20px; }
    h3 { color: #00ffcc !important; font-family: 'JetBrains Mono', monospace; border-bottom: 2px solid #1f2937; padding-bottom: 6px; }
    div[data-testid="stDataFrame"] { border: 1px solid #1f2937; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<div class='main-title'>⚡ ULTRA-FAST INTRADAY ALGO TERMINAL</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Multi-Threaded 5-Min Open=Low/High Scanner | Optimized Performance</div>", unsafe_allow_html=True)

if 'history_log' not in st.session_state:
    st.session_state.history_log = pd.DataFrame()

# 2. Parallel Processing Engine (High Speed)
def process_single_stock(symbol, df_all):
    try:
        df = df_all[symbol].dropna()
        if df.empty or len(df) < 1:
            return None
            
        c1 = df.iloc[0] 
        curr_price = float(df['Close'].iloc[-1]) 
        c1_open, c1_high, c1_low = float(c1['Open']), float(c1['High']), float(c1['Low'])
        
        candle_range_pct = ((c1_high - c1_low) / c1_open) * 100
        if candle_range_pct > 1.0:
            return None
            
        # BUY Logic
        if abs(c1_open - c1_low) < 0.05:
            entry, sl = c1_high, c1_low
            risk = entry - sl
            t1, t2 = entry + risk, entry + (risk * 1.5)
            status = "🎯 Pending"
            if curr_price >= entry:
                status = "🟢 Active Trade"
                if curr_price <= sl: status = "🔴 SL HIT"
                elif curr_price >= t2: status = "🎯 T2 HIT"
                elif curr_price >= t1: status = "✅ T1 HIT"
                    
            return {
                "Stock": symbol.replace(".NS", ""), "Type": "⚡ BUY (O=L)",
                "Entry Price": round(entry, 2), "StopLoss": round(sl, 2),
                "Target 1 (1:1)": round(t1, 2), "Target 2 (1:1.5)": round(t2, 2),
                "Current Price": round(curr_price, 2), "Status": status
            }
            
        # SELL Logic
        elif abs(c1_open - c1_high) < 0.05:
            entry, sl = c1_low, c1_high
            risk = sl - entry
            t1, t2 = entry - risk, entry - (risk * 1.5)
            status = "🎯 Pending"
            if curr_price <= entry:
                status = "🟢 Active Trade"
                if curr_price >= sl: status = "🔴 SL HIT"
                elif curr_price <= t2: status = "🎯 T2 HIT"
                elif curr_price <= t1: status = "✅ T1 HIT"
                    
            return {
                "Stock": symbol.replace(".NS", ""), "Type": "💥 SELL (O=H)",
                "Entry Price": round(entry, 2), "StopLoss": round(sl, 2),
                "Target 1 (1:1)": round(t1, 2), "Target 2 (1:1.5)": round(t2, 2),
                "Current Price": round(curr_price, 2), "Status": status
            }
    except:
        return None

@st.cache_data(ttl=45) # Cache data for 45 seconds to drastically reduce server load
def get_market_data():
    try:
        tickers = " ".join(all_stocks)
        return yf.download(tickers, period="1d", interval="5m", group_by='ticker', progress=False, timeout=10)
    except:
        return None

def scan_markets_fast():
    df_all = get_market_data()
    if df_all is None or df_all.empty:
        return pd.DataFrame()
        
    # Multi-threading for instantaneous calculations
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = executor.map(lambda s: process_single_stock(s, df_all), all_stocks)
        
    signals = [r for r in results if r is not None]
    return pd.DataFrame(signals)

# Run fast engine
df_results = scan_markets_fast()

if not df_results.empty:
    st.session_state.history_log = df_results.copy()

# 3. Clean Dual Dashboard UI Layout
col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader("⚡ Live Market Dashboard")
    if not df_results.empty:
        df_live_only = df_results[df_results['Status'].isin(["🟢 Active Trade", "🎯 Pending"])]
        if not df_live_only.empty:
            st.dataframe(df_live_only, use_container_width=True, hide_index=True)
        else:
            st.info("No active trades running at this second.")
    else:
        st.info("Looking for price breakout setups...")

with col_right:
    st.subheader("📚 Daily History Summary Log")
    if not st.session_state.history_log.empty:
        st.dataframe(st.session_state.history_log, use_container_width=True, hide_index=True)
    else:
        st.info("No signals captured yet today.")

# 4. Smart Non-blocking Sleep
time.sleep(60)
st.rerun()
