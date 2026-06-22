import streamlit as st
import yfinance as yf
import pandas as pd
import time

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

# 1. Page Configuration & Professional CSS Styling
st.set_page_config(page_title="Pro Intraday Algo Terminal", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');
    
    /* Main App Background */
    .stApp { background-color: #080b10; font-family: 'Segoe UI', sans-serif; }
    
    /* Header Styling */
    .main-title { color: #00ffcc; text-align: center; font-size: 36px; font-weight: 800; letter-spacing: 1px; margin-bottom: 5px; text-shadow: 0 0 20px rgba(0, 255, 204, 0.4); }
    .sub-title { color: #8a99ad; text-align: center; font-size: 15px; margin-bottom: 25px; }
    
    /* Block Headers */
    h3 { color: #00ffcc !important; font-family: 'JetBrains Mono', monospace; border-bottom: 1px solid #1f2937; padding-bottom: 8px; margin-top: 20px !important; }
    
    /* Dropdown UI Customization */
    .stSelectbox label { color: #00ffcc !important; font-weight: bold; }
    
    /* Interactive Iframe Widget Container */
    iframe { border: 2px solid #00ffcc !important; border-radius: 12px; box-shadow: 0 0 15px rgba(0, 255, 204, 0.15); }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<div class='main-title'>⚡ PRO INTRADAY ALGO SCANNER TERMINAL </div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Advanced 5-Min Open=Low/High Engine | Live Tracking Dashboard | Auto-Refresh: 60s</div>", unsafe_allow_html=True)

# Initialize Session State to maintain history persistently across reruns
if 'history_log' not in st.session_state:
    st.session_state.history_log = pd.DataFrame()

# 2. Optimized Batch Scanning Engine
def scan_markets_fast():
    signals = []
    try:
        tickers = " ".join(all_stocks)
        df_all = yf.download(tickers, period="1d", interval="5m", group_by='ticker', progress=False)
    except Exception as e:
        st.error(f"Error fetching data from Yahoo Finance: {e}")
        return pd.DataFrame()

    for symbol in all_stocks:
        try:
            df = df_all[symbol].dropna()
            if df.empty or len(df) < 1:
                continue
                
            c1 = df.iloc[0] 
            curr_price = float(df['Close'].iloc[-1]) 
            
            c1_open = float(c1['Open'])
            c1_high = float(c1['High'])
            c1_low = float(c1['Low'])
            
            candle_range_pct = ((c1_high - c1_low) / c1_open) * 100
            clean_name = symbol.replace(".NS", "")
            
            if candle_range_pct <= 1.0:
                # --- OPEN = LOW (BUY STRATEGY) ---
                if abs(c1_open - c1_low) < 0.05:
                    entry = c1_high
                    sl = c1_low
                    risk = entry - sl
                    t1 = entry + risk
                    t2 = entry + (risk * 1.5)
                    
                    status = "🎯 Pending"
                    if curr_price >= entry:
                        status = "🟢 Active Trade"
                        if curr_price <= sl: status = "🔴 SL HIT"
                        elif curr_price >= t2: status = "🎯 T2 HIT"
                        elif curr_price >= t1: status = "✅ T1 HIT"
                            
                    signals.append({
                        "Stock": clean_name,
                        "Type": "BUY 🟢",
                        "Entry Price": round(entry, 2),
                        "StopLoss": round(sl, 2),
                        "Target 1": round(t1, 2),
                        "Target 2": round(t2, 2),
                        "Current Price": round(curr_price, 2),
                        "Status": status
                    })
                
                # --- OPEN = HIGH (SELL STRATEGY) ---
                elif abs(c1_open - c1_high) < 0.05:
                    entry = c1_low
                    sl = c1_high
                    risk = sl - entry
                    t1 = entry - risk
                    t2 = entry - (risk * 1.5)
                    
                    status = "🎯 Pending"
                    if curr_price <= entry:
                        status = "🟢 Active Trade"
                        if curr_price >= sl: status = "🔴 SL HIT"
                        elif curr_price <= t2: status = "🎯 T2 HIT"
                        elif curr_price <= t1: status = "✅ T1 HIT"
                            
                    signals.append({
                        "Stock": clean_name,
                        "Type": "SELL 🔴",
                        "Entry Price": round(entry, 2),
                        "StopLoss": round(sl, 2),
                        "Target 1": round(t1, 2),
                        "Target 2": round(t2, 2),
                        "Current Price": round(curr_price, 2),
                        "Status": status
                    })
        except:
            continue
            
    return pd.DataFrame(signals)

# Trigger Engine Processing
df_results = scan_markets_fast()

# Update Session State History persistently
if not df_results.empty:
    st.session_state.history_log = df_results.copy()

# Real-time System Toast Alerts
if not df_results.empty:
    for _, row in df_results.iterrows():
        if "HIT" in row["Status"]:
            st.toast(f"🚨 {row['Stock']}: {row['Status']}!", icon="📢")
        elif "Active" in row["Status"]:
            st.toast(f"🚀 Execution Triggered: {row['Stock']}", icon="🔥")

# 3. Double Panel Layout Structure
col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader("⚡ Live Market Dashboard")
    # Filters out only active and pending trades to showcase focused live action
    if not df_results.empty:
        df_live_display = df_results[df_results['Status'].isin(["🟢 Active Trade", "🎯 Pending"])]
        if not df_live_display.empty:
            st.dataframe(df_live_display, use_container_width=True, hide_index=True)
        else:
            st.info("No trades currently active or pending. Check out the history log below.")
    else:
        st.info("Scanning live order book... Waiting for market data triggers.")

with col_right:
    st.subheader("📚 Daily History Summary Log")
    if not st.session_state.history_log.empty:
        st.dataframe(st.session_state.history_log, use_container_width=True, hide_index=True)
    else:
        st.write("No signals recorded for today yet.")

st.markdown("---")

# 4. Error-Free HD TradingView Integration
st.subheader("📈 HD Multi-Tool Chart Terminal")
if not st.session_state.history_log.empty:
    selected_stock = st.selectbox("Select a Stock to Load Chart:", st.session_state.history_log['Stock'].unique())
    
    # Clean up and force standardized TV syntax to resolve the 'image_90c799.png' error
    tv_widget_html = f"""
    <div class="tradingview-widget-container" style="height:680px; width:100%;">
      <div id="tradingview_dashboard_terminal"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">
      new TradingView.widget({{
        "autosize": true,
        "symbol": "NSE:{selected_stock}",
        "interval": "5",
        "timezone": "Asia/Kolkata",
        "theme": "dark",
        "style": "1",
        "locale": "en",
        "toolbar_bg": "#f1f3f6",
        "enable_publishing": false,
        "hide_side_toolbar": false,
        "allow_symbol_change": true,
        "container_id": "tradingview_dashboard_terminal"
      }});
      </script>
    </div>
    """
    st.components.v1.html(tv_widget_html, height=690)
else:
    st.info("Charts layout module will activate instantly once stocks pass criteria loops.")

# 5. Smart Refresh Mechanism
time.sleep(60)
st.rerun()
