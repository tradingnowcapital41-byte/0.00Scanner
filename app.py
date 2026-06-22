import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import time

# सर्व स्टॉक्सची योग्य लिस्ट
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

# १. डॅशबोर्ड कॉन्फिगरेशन आणि CSS लुक
st.set_page_config(page_title="Ultimate Pro Scanner", layout="wide")

st.markdown("""
    <style>
    .reportview-container { background: #0b0e14; }
    h1 { color: #00ffcc !important; text-align: center; text-shadow: 0 0 15px #00ffcc; font-family: 'Segoe UI', sans-serif; font-weight: 800; }
    h3 { color: #ffffff !important; border-bottom: 2px solid #00ffcc; padding-bottom: 5px; }
    .stButton>button { background-color: #00ffcc; color: black; font-weight: bold; width: 100%; border-radius: 8px; box-shadow: 0 4px 15px rgba(0,255,204,0.3); }
    iframe { border: 2px solid #00ffcc !important; border-radius: 12px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1>📊 INTRADAY ALGO TERMINAL (OPEN=LOW/HIGH)</h1>", unsafe_allow_html=True)

# Session State मध्ये हिस्ट्री डेटा कायम ठेवण्यासाठी
if 'trade_history' not in st.session_state:
    st.session_state.trade_history = pd.DataFrame()

# २. वेगवान डेटा फेटचिंग फंक्शन
def scan_and_process():
    live_trades = []
    try:
        tickers = " ".join(all_stocks)
        df_all = yf.download(tickers, period="1d", interval="5m", group_by='ticker', progress=False, timeout=15)
    except:
        return pd.DataFrame()

    for symbol in all_stocks:
        try:
            df = df_all[symbol].dropna()
            if df.empty or len(df) < 1: continue
                
            c1 = df.iloc[0]
            curr_price = float(df['Close'].iloc[-1])
            c1_open, c1_high, c1_low = float(c1['Open']), float(c1['High']), float(c1['Low'])
            candle_range_pct = ((c1_high - c1_low) / c1_open) * 100
            
            clean_name = symbol.replace(".NS", "")
            
            if candle_range_pct <= 1.0:
                # BUY Strategy (O=L)
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
                            
                    live_trades.append({"Stock": clean_name, "Type": "BUY 🟢", "Entry Price": round(entry, 2), "StopLoss": round(sl, 2), "Target 1": round(t1, 2), "Target 2": round(t2, 2), "Current Price": round(curr_price, 2), "Status": status})
                
                # SELL Strategy (O=H)
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
                            
                    live_trades.append({"Stock": clean_name, "Type": "SELL 🔴", "Entry Price": round(entry, 2), "StopLoss": round(sl, 2), "Target 1": round(t1, 2), "Target 2": round(t2, 2), "Current Price": round(curr_price, 2), "Status": status})
        except: continue
    return pd.DataFrame(live_trades)

# मार्केट स्कॅनिंग सुरू करा
df_live = scan_and_process()

# ३. डॅशबोर्ड मांडणी (Layout)
col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("⚡ Live Signal & Tracking Panel")
    if not df_live.empty:
        st.dataframe(df_live, use_container_width=True, hide_index=True)
        
        # हिस्टरी अपडेट लॉजिक (फक्त ट्रिगर झालेले किंवा क्लोज झालेले ट्रेड्स सेव्ह होतील)
        st.session_state.trade_history = df_live.copy()
        
        # पॉप-अप अलर्ट
        for _, row in df_live.iterrows():
            if "HIT" in row["Status"]:
                st.toast(f"⚠️ ALERT: {row['Stock']} चा {row['Status']} झालाय!", icon="📢")
    else:
        st.info("अटींमध्ये बसणारा कोणताही लाईव्ह स्टॉक सापडला नाही. (मार्केट चालू असताना तपासा)")

with col_right:
    st.subheader("🎯 Performance Metrics")
    if not st.session_state.trade_history.empty:
        status_counts = st.session_state.trade_history['Status'].value_counts().reset_index()
        status_counts.columns = ['Status', 'Count']
        fig = px.pie(status_counts, values='Count', names='Status', 
                     color_discrete_map={'🔴 SL HIT':'#ff4d4d', '✅ T1 HIT':'#2ecc71', '🎯 T2 HIT':'#1abc9c', '🟢 Active Trade':'#f1c40f', '🎯 Pending':'#95a5a6'}, hole=0.3)
        fig.update_layout(margin=dict(t=10, b=10, l=10, r=10), paper_bgcolor='rgba(0,0,0,0)', font_color="white", height=220)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.write("डेटा लोड होत आहे...")

st.markdown("---")

# ४. 📈 एरर-फ्री HD TRADINGVIEW PANEL (Fixed Symbol Error)
st.subheader("🔍 HD TradingView Terminal")
if not st.session_state.trade_history.empty:
    selected_stock = st.selectbox("चार्ट पाहण्यासाठी स्टॉक निवडा:", st.session_state.trade_history['Stock'].unique())
    
    # गुंतागुंतीचे सिम्बॉल फिक्स करण्यासाठी सरळ NSE: फॉरमॅटचा अधिकृत विजेट वापरला आहे
    tv_widget_html = f"""
    <div class="tradingview-widget-container" style="height:650px; width:100%;">
      <div id="tradingview_dashboard"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">
      new TradingView.widget({{
        "autosize": true,
        "symbol": "NSE:{selected_stock}",
        "interval": "5",
        "timezone": "Asia/Kolkata",
        "theme": "dark",
        "style": "1",
        "locale": "in",
        "toolbar_bg": "#f1f3f6",
        "enable_publishing": false,
        "hide_side_toolbar": false,
        "allow_symbol_change": true,
        "container_id": "tradingview_dashboard"
      }});
      </script>
    </div>
    """
    st.components.v1.html(tv_widget_html, height=660)
else:
    st.info("सिग्नल्स लोड झाल्यावर चार्ट सिलेक्ट करण्याचा पर्याय येथे सुरू होईल.")

# ५. दिवसभराची स्वतंत्र 'History Panel' (खाली वेगळा टेबल)
st.markdown("---")
st.subheader("📚 आजची पूर्ण ट्रेड हिस्टरी (Daily History Summary)")
if not st.session_state.trade_history.empty:
    st.dataframe(st.session_state.trade_history, use_container_width=True, hide_index=True)
else:
    st.write("अजून हिस्टरी तयार झालेली नाही.")

# ६० सेकंदांचा ऑटो-अपडेट जो क्रॅश रोखतो
time.sleep(60)
st.rerun()
