import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px

# सर्व १०० स्टॉक्सची लिस्ट
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

# १. पेज सेटअप आणि कस्टमायझेशन (HTML/CSS)
st.set_page_config(page_title="Pro Open=Low/High Terminal", layout="wide")

# CSS चा तडका - डार्क थीम आणि ग्लॅमरस प्रीमियम लुक
st.markdown("""
    <style>
    .reportview-container { background: #0e1117; }
    h1 { color: #00ffcc !important; font-family: 'Segoe UI', sans-serif; text-align: center; text-shadow: 0 0 10px #00ffcc; }
    .stButton>button { background-color: #00ffcc; color: black; font-weight: bold; border-radius: 8px; border: none; box-shadow: 0 4px 15px rgba(0,255,204,0.4); }
    .stButton>button:hover { background-color: #00ccaa; color: white; }
    div[data-testid="stMetricValue"] { color: #00ffcc !important; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1>⚡ PRO EQUITY STOCK SCANNER Terminal ⚡</h1>", unsafe_allow_html=True)
st.caption("<p style='text-align: center; color: #888;'>Premium Auto-Scanner with Live TradingView Charts & Performance Metrics (Auto-refresh every 60s)</p>", unsafe_allow_html=True)

# २. मार्केट स्कॅनिंग लॉजिक
def scan_markets_fast():
    signals = []
    try:
        tickers = " ".join(all_stocks)
        df_all = yf.download(tickers, period="1d", interval="5m", group_by='ticker', progress=False)
    except Exception as e:
        return pd.DataFrame()

    for symbol in all_stocks:
        try:
            df = df_all[symbol].dropna()
            if df.empty or len(df) < 1: continue
                
            c1 = df.iloc[0]
            curr_price = float(df['Close'].iloc[-1])
            c1_open, c1_high, c1_low = float(c1['Open']), float(c1['High']), float(c1['Low'])
            candle_range_pct = ((c1_high - c1_low) / c1_open) * 100
            
            if candle_range_pct <= 1.0:
                # BUY (O=L)
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
                            
                    signals.append({"Stock": symbol.replace(".NS", ""), "Type": "BUY", "Entry": round(entry, 2), "SL": round(sl, 2), "Target 1": round(t1, 2), "Target 2": round(t2, 2), "Current": round(curr_price, 2), "Status": status})
                
                # SELL (O=H)
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
                            
                    signals.append({"Stock": symbol.replace(".NS", ""), "Type": "SELL", "Entry": round(entry, 2), "SL": round(sl, 2), "Target 1": round(t1, 2), "Target 2": round(t2, 2), "Current": round(curr_price, 2), "Status": status})
        except: continue
    return pd.DataFrame(signals)

df_results = scan_markets_fast()

# ३. लेआउट मॅनेजमेंट (डावीकडे टेबल आणि उजवीकडे पाई चार्ट)
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📊 आजचे लाईव्ह सिग्नल्स")
    if not df_results.empty:
        st.dataframe(df_results, use_container_width=True, hide_index=True)
        for _, row in df_results.iterrows():
            if "HIT" in row["Status"]:
                st.toast(f"⚠️ {row['Stock']}: {row['Status']}!", icon="📢")
    else:
        st.info("अटींमध्ये बसणारा कोणताही स्टॉक सध्या नाही. (९:२० नंतर चेक करा)")

with col2:
    st.subheader("📈 आजची कामगिरी (Win/Loss)")
    if not df_results.empty:
        # स्टॅटिस्टिक्स मोजणे
        status_counts = df_results['Status'].value_counts().reset_index()
        status_counts.columns = ['Status', 'Count']
        
        # भारी कलर्ससह विजुअल पाई चार्ट
        fig = px.pie(status_counts, values='Count', names='Status', 
                     color_discrete_map={'🔴 SL HIT':'#ff4d4d', '✅ T1 HIT':'#2ecc71', '🎯 T2 HIT':'#1abc9c', '🟢 Active Trade':'#f1c40f', '🎯 Pending':'#95a5a6'},
                     hole=0.4)
        fig.update_layout(showlegend=True, margin=dict(t=0, b=0, l=0, r=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.write("डेटा उपलब्ध नाही.")

st.markdown("---")

# ४. 📈 MINI TRADINGVIEW CHART INTEGRATION
st.subheader("🔍 लाईव्ह टेक्निकल चार्ट (TradingView)")
if not df_results.empty:
    selected_stock = st.selectbox("कोणत्या स्टॉकचा ५-मिनिटांचा चार्ट पाहायचा आहे? निवडा:", df_results['Stock'].unique())
    
    # TradingView चं मोफत विजेट जे इंडिकेटर्स (RSI, VWAP) ला सपोर्ट करतं
    tv_widget_html = f"""
    <div class="tradingview-widget-container" style="height:500px;">
      <div id="tradingview_chart"></div>
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
        "studies": [
          "RSI@tv-basicstudies",
          "VWAP@tv-basicstudies"
        ],
        "container_id": "tradingview_chart"
      }});
      </script>
    </div>
    """
    st.components.v1.html(tv_widget_html, height=520)
else:
    st.info("चार्ट पाहण्यासाठी आधी सिग्नल्स उपलब्ध असणे आवश्यक आहे.")

# ऑटो-अपडेट ६० सेकंद
import time
time.sleep(60)
st.rerun()
