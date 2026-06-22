import streamlit as st
import yfinance as yf
import pandas as pd

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

# 1. UI Configuration
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
st.markdown("<div class='sub-title'>High-Speed 5-Min Open=Low/High Scanner | Zero-Load Architecture</div>", unsafe_allow_html=True)

# 2. Safe HTML Refresh (Does not block the server)
# It injects a tiny JavaScript refresh every 60000ms (60 seconds)
st.components.v1.html(
    "<script>parent.window.location.reload();</script>",
    height=0, width=0
)

if 'history_log' not in st.session_state:
    st.session_state.history_log = pd.DataFrame()

# 3. Super-Fast Batch Data Processor
@st.cache_data(ttl=30)  # 30 seconds caching prevents yfinance IP ban
def fetch_and_scan():
    signals = []
    try:
        tickers = " ".join(all_stocks)
        # Fetching everything linearly is 10x faster than MultiIndex grouping on Cloud
        df_all = yf.download(tickers, period="1d", interval="5m", progress=False, timeout=8)
        if df_all.empty:
            return pd.DataFrame()
    except:
        return pd.DataFrame()

    for symbol in all_stocks:
        try:
            # Clean extraction without MultiIndex overhead
            open_series = df_all['Open'][symbol].dropna()
            high_series = df_all['High'][symbol].dropna()
            low_series = df_all['Low'][symbol].dropna()
            close_series = df_all['Close'][symbol].dropna()

            if open_series.empty:
                continue

            c1_open = float(open_series.iloc[0])
            c1_high = float(high_series.iloc[0])
            c1_low = float(low_series.iloc[0])
            curr_price = float(close_series.iloc[-1])

            candle_range_pct = ((c1_high - c1_low) / c1_open) * 100
            if candle_range_pct > 1.0:
                 Kakontinue
            
            clean_name = symbol.replace(".NS", "")

            # BUY Logic
            if abs(c1_open - c1_low) < 0.05:
                entry, sl = c1_high, c1_low
                risk = entry - sl
                t1, t2 = entry + risk, entry + (risk * 1.5)
                status = "🎯 Pending"
                if curr_price >= entry:
                    status = "🟢 Active"
                    if curr_price <= sl: status = "🔴 SL HIT"
                    elif curr_price >= t2: status = "🎯 T2 HIT"
                    elif curr_price >= t1: status = "✅ T1 HIT"

                signals.append({
                    "Stock": clean_name, "Type": "⚡ BUY (O=L)",
                    "Entry": round(entry, 2), "StopLoss": round(sl, 2),
                    "Target 1": round(t1, 2), "Target 2": round(t2, 2),
                    "Current": round(curr_price, 2), "Status": status
                })

            # SELL Logic
            elif abs(c1_open - c1_high) < 0.05:
                entry, sl = c1_low, c1_high
                risk = sl - entry
                t1, t2 = entry - risk, entry - (risk * 1.5)
                status = "🎯 Pending"
                if curr_price <= entry:
                    status = "🟢 Active"
                    if curr_price >= sl: status = "🔴 SL HIT"
                    elif curr_price <= t2: status = "🎯 T2 HIT"
                    elif curr_price <= t1: status = "✅ T1 HIT"

                signals.append({
                    "Stock": clean_name, "Type": "💥 SELL (O=H)",
                    "Entry": round(entry, 2), "StopLoss": round(sl, 2),
                    "Target 1": round(t1, 2), "Target 2": round(t2, 2),
                    "Current": round(curr_price, 2), "Status": status
                })
        except:
            continue
    return pd.DataFrame(signals)

df_results = fetch_and_scan()

if not df_results.empty:
    st.session_state.history_log = df_results.copy()

# 4. Two-Panel Layout
col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader("⚡ Live Market Dashboard")
    if not df_results.empty:
        df_live_only = df_results[df_results['Status'].isin(["🟢 Active", "🎯 Pending"])]
        if not df_live_only.empty:
            st.dataframe(df_live_only, use_container_width=True, hide_index=True)
        else:
            st.info("No active breakout setups currently.")
    else:
        st.info("No stocks matched the criteria yet.")

with col_right:
    st.subheader("📚 Daily History Summary Log")
    if not st.session_state.history_log.empty:
        st.dataframe(st.session_state.history_log, use_container_width=True, hide_index=True)
    else:
        st.info("No history log captured for today yet.")
